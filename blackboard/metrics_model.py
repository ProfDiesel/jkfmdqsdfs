from __future__ import annotations

import asyncio
from typing import NewType, TypeAlias
from dataclasses import dataclass
from scipy.spatial.distance import cosine
from contextlib import contextmanager

from sqlalchemy import ForeignKey, JSON, select, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import create_async_engine

import usearch
import numpy
import orjson

from functools import partial


DocKey = NewType('DocKey', int)
ReqKey = NewType('ReqKey', int)


@dataclass
class ElasictId:
    index: str
    id: int

@dataclass
class SqliteId:
    table: str
    key: int

DocId: TypeAlias = ElasictId | SqliteId

Embedding: TypeAlias = numpy.array

class Base(DeclarativeBase):
    pass

class Attribution(Base):
    __tablename__ = "attribution"

    doc: Mapped[DocKey] = mapped_column(ForeignKey('document.id'), primary_key=True, type_=Integer)
    req: Mapped[ReqKey] = mapped_column(ForeignKey('request.id'), primary_key=True)

    utilization: Mapped[float] # cosine_similarity(doc.embedding, req.response_embedding)
    store_score: Mapped[float]
    consolidated_score: Mapped[float]
    ragas_score: Mapped[float | None]

    document: Mapped[Document] = relationship(back_populates='attributions')
    request: Mapped[Request] = relationship(back_populates='attributions')


class Document(Base):
    __tablename__ = "document"

    id: Mapped[DocKey] = mapped_column(primary_key=True, type_=Integer)
    document_id: Mapped[DocId] = mapped_column(JSON)
    embedding: Mapped[Embedding] = mapped_column(JSON)

    # request: Mapped[Request] = relationship('attribution', back_populates='request')
    attributions: Mapped[set[Attribution]] = relationship(back_populates='document')


class Request(Base):
    __tablename__ = "request"

    id: Mapped[ReqKey] = mapped_column(primary_key=True, type_=Integer)
    query_embedding: Mapped[Embedding] = mapped_column(JSON)
    context_embedding: Mapped[Embedding] = mapped_column(JSON)
    response_embedding: Mapped[Embedding] = mapped_column(JSON)
    
    attributions: Mapped[set[Attribution]] = relationship(back_populates='request')


class Metrics:
    def __init__(self):
        engine = create_async_engine("sqlite+aiosqlite:///metrics.db", json_serializer=partial(orjson.dumps, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS))
        engine.echo = True
        self.__async_session = async_sessionmaker(engine)

    async def init(self):
        async with self.session() as session:
            async with session.begin():
                await session.run_sync(Base.metadata.create_all)

    @contextmanager
    async def session(self):
        async with self.__async_session() as session:
            connection = await session.connection()
            driver_connection = (await connection.get_raw_connection()).driver_connection
            await driver_connection.enable_load_extension(True)
            await driver_connection.load_extension(usearch.sqlite_path())
            yield session


async def attribution(session: AsyncSession, doc: DocKey):
    statement = select(func.count(Attribution.utilization)).where(Attribution.doc == doc)
    return await session.scalar(statement)

async def utilization(session: AsyncSession, doc: DocKey):
    all_utilizations = select(Attribution.utilization).where(Attribution.doc == doc).scalar_subquery()
    statement = select(func.sum(all_utilizations) / func.count(all_utilizations))
    return await session.scalar(statement)

async def completeness_proxy(session: AsyncSession, req: ReqKey):
    "utillization of docs by request response"
    all_utilizations = select(Attribution.utilization).where(Attribution.req == req).scalar_subquery()
    statement = select(func.sum(all_utilizations) / func.count(all_utilizations))
    return await session.scalar(statement)
    
async def context_adherence_proxy(session: AsyncSession, req: ReqKey):
    statement = select(func.distance_cosine_f32(Request.context_embedding, Request.response_embedding)).where(Request.id == req)
    return await session.scalar(statement)

async def test():
    metrics = Metrics()
    await metrics.init()
    async with metrics.session() as session:
        async with session.begin():
            session.add_all([
                Document(id=0, document_id=ElasictId(index='index', id=0), embedding=Embedding([1, 2, 3])),
                Document(id=1, document_id=ElasictId(index='index', id=1), embedding=Embedding([4, 5, 6])),
                Request(id=0, query_embedding=Embedding([1, 2, 3]), context_embedding=Embedding([4, 5, 6]), response_embedding=Embedding([7, 8, 9])),
                Attribution(doc=0, req=0, utilization=0.1, store_score=0.8, consolidated_score=0.5, ragas_score=0.2),
                Attribution(doc=1, req=0, utilization=0.1, store_score=0.8, consolidated_score=0.5, ragas_score=0.2)])

        # print('attribution 0', await attribution(session, 0))
        # print('attribution 1', await attribution(session, 1))
        # print('utilization 0', await utilization(session, 0))
        # print('utilization 0', await utilization(session, 1))
        # print('completeness 1', await completeness_proxy(session, 0))
        print('adherence 0', await context_adherence_proxy(session, 0))

