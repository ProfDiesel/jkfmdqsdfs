#!/usr/bin/env bash

cat $(dirname ${BASH_SOURCE})/create_table.sql | TABLE=jiras DIMENSIONALITY=100 envsubst | sqlite vss.db -