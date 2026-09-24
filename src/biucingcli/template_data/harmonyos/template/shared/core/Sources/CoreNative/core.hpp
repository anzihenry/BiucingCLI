#pragma once

#include <cstddef>
#include <cstdint>

namespace biucing::core {
// Caller validates the pointer/count pair. Returns false on overflow.
bool checked_sum(const std::int64_t *values, std::size_t count,
                 std::int64_t &result) noexcept;
}
