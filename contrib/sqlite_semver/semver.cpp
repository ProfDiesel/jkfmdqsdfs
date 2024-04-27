// g++ -std=gnu++26 -I. -fPIC --shared semver.cpp -o semver
#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

// https://github.com/z4kn4fein/cpp-semver.git
#include <semver.hpp>

static bool is_utf8(const unsigned char *s) {
    for(auto it = s; *it; ++it) if(*it > 127) return false;
    return true;
}

static void semvercmp(sqlite3_context *context, int argc, sqlite3_value **argv) {
    auto lhs = sqlite3_value_text(argv[0]);
    auto rhs = sqlite3_value_text(argv[1]);
    sqlite3_result_int(context, is_utf8(lhs) && is_utf8(rhs) ? semver::version::parse(reinterpret_cast<const char*>(lhs))<=> semver::version::parse(reinterpret_cast<const char*>(rhs)) : 0);
}

extern "C" int sqlite3_semver_init(sqlite3 *db, char **pzErrMsg, const sqlite3_api_routines *pApi) {
    SQLITE_EXTENSION_INIT2(pApi);
    return sqlite3_create_function(db, "semvercmp", 2, SQLITE_UTF8 | SQLITE_INNOCUOUS | SQLITE_DETERMINISTIC, nullptr, semvercmp, nullptr, nullptr);
}
