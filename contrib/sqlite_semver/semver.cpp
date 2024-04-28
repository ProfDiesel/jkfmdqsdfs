// g++ -std=gnu++26 -I. -fPIC --shared semver.cpp -o semver
#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

// https://github.com/z4kn4fein/cpp-semver.git
#include <semver.hpp>

static bool is_utf8(const char *s) {
    for(auto it = s; *it; ++it) if(*it < 0) return false;
    return true;
}

static int semvercollate(void *userdata, int lhs_length, const void *lhs_raw, int rhs_length, const void *rhs_raw) {
    auto lhs = reinterpret_cast<const char*>(lhs_raw);
    auto rhs = reinterpret_cast<const char*>(rhs_raw);
    return is_utf8(lhs) && is_utf8(rhs) ? semver::version::parse(lhs)<=> semver::version::parse(rhs) : 0;
}

static void semvercmp(sqlite3_context *context, int argc, sqlite3_value **argv) {
    auto lhs = sqlite3_value_text(argv[0]);
    auto rhs = sqlite3_value_text(argv[1]);
    sqlite3_result_int(semvercollate(nullptr, 0, lhs, 0, rhs));
}

extern "C" int sqlite3_semver_init(sqlite3 *db, char **pzErrMsg, const sqlite3_api_routines *pApi) {
    SQLITE_EXTENSION_INIT2(pApi);
    if(int rc = sqlite3_create_function(db, "semvercmp", 2, SQLITE_UTF8 | SQLITE_INNOCUOUS | SQLITE_DETERMINISTIC, nullptr, semvercmp, nullptr, nullptr); rc != SQLITE_OK)
        return rc;
    if(int rc = sqlite3_create_collation(db, "semvercollate", 2, SQLITE_UTF8 | SQLITE_INNOCUOUS | SQLITE_DETERMINISTIC, nullptr, semvercollate); rc != SQLITE_OK)
        return rc;
    return SQLITE_OK;
}
