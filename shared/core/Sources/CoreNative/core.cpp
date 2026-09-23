#include "core.hpp"

#include <limits>

namespace biucing::core {
bool checked_sum(const std::int64_t *values, std::size_t count,
                 std::int64_t &result) noexcept {
    std::int64_t total = 0;
    for (std::size_t index = 0; index < count; ++index) {
        const auto value = values[index];
        if ((value > 0 && total > std::numeric_limits<std::int64_t>::max() - value) ||
            (value < 0 && total < std::numeric_limits<std::int64_t>::min() - value)) {
            return false;
        }
        total += value;
    }
    result = total;
    return true;
}
}
