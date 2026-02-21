# C++跨平台技术栈详细文档

## 概述

本文档详细介绍了我们推荐的C++跨平台技术栈，该技术栈以现代C++23标准为核心，结合CMake构建系统和一系列高效的开发工具。这个组合提供了高性能、跨平台的桌面应用程序开发解决方案，支持Windows、Linux和macOS等多个操作系统。

## 技术栈组成

### 1. 核心语言 (C++23)

#### C++23
- **版本**: C++23标准
- **作用**: 现代C++编程语言标准
- **优势**:
  - 模式匹配(std::expected)改进错误处理
  - std::flat_map和std::flat_set提供更好的性能
  - 通用lambda捕获简化代码编写
  - 范围适配器改进算法使用
  - 更好的constexpr支持
  - 模块化支持进一步完善

### 2. 构建系统

#### CMake
- **版本**: 4.0+
- **作用**: 跨平台构建系统生成器
- **优势**:
  - 支持多平台构建（Windows, Linux, macOS）
  - 丰富的模块和工具链支持
  - 与主流IDE良好集成
  - 强大的依赖管理和包管理功能
  - 可生成多种构建系统文件（Makefile, Ninja, Visual Studio等）
  - 更好的C++23标准支持

#### Ninja
- **作用**: 小型构建系统，专注于速度
- **优势**:
  - 极快的构建速度
  - 低内存占用
  - 与CMake无缝集成
  - 并行构建支持

### 3. 包管理器

#### Conan
- **作用**: C/C++包管理器，专为现代C++设计
- **优势**:
  - 支持多平台和多编译器
  - 丰富的预构建包生态
  - 灵活的依赖管理
  - 与CMake等构建系统集成
  - 支持私有仓库

#### vcpkg
- **作用**: C++库管理器，微软开源项目
- **优势**:
  - 与Visual Studio集成良好
  - 大量预构建库
  - 跨平台支持（Windows, Linux, macOS）
  - 简单的安装和管理命令

### 4. 编译器

#### Clang
- **作用**: 基于LLVM的C++编译器
- **优势**:
  - 优秀的错误和警告信息
  - 高性能编译
  - 良好的C++23标准支持
  - 静态分析工具集成
  - 跨平台支持

#### GCC
- **作用**: GNU编译器集合，广泛使用的C++编译器
- **优势**:
  - 成熟稳定的编译器
  - 强大的C++23标准支持
  - 优化性能出色
  - 广泛的平台支持

#### MSVC
- **作用**: Microsoft Visual C++编译器
- **优势**:
  - 与Windows平台深度集成
  - 优秀的调试支持
  - 与Visual Studio IDE完美配合
  - 对Windows API的良好支持

### 5. 框架和库

#### Boost
- **作用**: 综合性的C++库集合
- **优势**:
  - 提供标准库之外的高级功能
  - 跨平台的实用工具库
  - 高质量的模板库
  - 广泛的社区支持
  - 许多功能后来被纳入C++标准

### 6. 测试框架

#### Catch2
- **作用**: 现代C++测试框架
- **优势**:
  - 单头文件，易于集成
  - BDD/TDD风格的测试编写
  - 丰富的断言宏
  - 自动测试注册
  - 优秀的错误报告

### 7. 日志系统

#### spdlog
- **作用**: 高性能C++日志库
- **优势**:
  - 极快的日志记录速度
  - 线程安全
  - 支持多种输出格式
  - 异步日志记录
  - 轻量级设计

### 8. 格式化库

#### fmt
- **作用**: 现代C++格式化库
- **优势**:
  - 类似Python的格式化语法
  - 高性能字符串格式化
  - 类型安全
  - 支持用户自定义类型
  - 被C++23采纳为std::format的基础

## 项目结构

```
cpp-cross-platform-project/
├── CMakeLists.txt                 # 顶层CMake配置
├── CMakePresets.json             # CMake配置预设
├── conanfile.txt                 # Conan依赖配置
├── vcpkg-configuration.json      # vcpkg配置
├── .gitignore
├── README.md
├── src/                         # 源代码目录
│   ├── main.cpp                 # 应用程序入口
│   ├── core/                    # 核心业务逻辑
│   │   ├── application.cpp
│   │   ├── application.h
│   │   ├── config.cpp
│   │   └── config.h
│   ├── ui/                      # 用户界面相关（如使用其他GUI框架）
│   │   ├── mainwindow.cpp
│   │   ├── mainwindow.h
│   │   └── widgets/             # 自定义控件
│   ├── utils/                   # 工具函数
│   │   ├── logger.cpp
│   │   ├── logger.h
│   │   └── helpers.h
│   ├── models/                  # 数据模型
│   │   ├── datamodel.cpp
│   │   └── datamodel.h
│   └── tests/                   # 单元测试
│       ├── test_main.cpp        # 测试入口
│       ├── test_core.cpp
│       └── test_utils.cpp
├── include/                     # 公共头文件
│   └── myproject/               # 项目头文件
├── resources/                   # 资源文件
│   ├── icons/                   # 图标文件
│   └── translations/            # 翻译文件
├── docs/                        # 文档
├── cmake/                       # 自定义CMake模块
│   └── FindCustomLib.cmake
├── scripts/                     # 构建和部署脚本
│   ├── build.sh
│   ├── deploy.sh
│   └── test.sh
├── third-party/                 # 第三方库（如果需要手动管理）
└── build/                       # 构建输出目录（通常在.gitignore中）
```

## 开发工作流

### 环境准备

```bash
# 安装CMake
# Windows: choco install cmake
# Ubuntu: sudo apt install cmake
# macOS: brew install cmake

# 安装编译器
# Windows: Visual Studio 2022 或 MinGW-w64
# Ubuntu: sudo apt install build-essential
# macOS: xcode-select --install

# 安装包管理器（选择其一）
# Conan
pip install conan

# 或 vcpkg
git clone https://github.com/Microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.sh
```

### 构建项目

```bash
# 使用CMake构建
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .

# 或使用CMake Presets（推荐）
cmake --preset=dev
cmake --build --preset=dev

# 运行测试
ctest

# 或直接运行可执行文件
./bin/myapp
```

### 使用Conan管理依赖

```bash
# 安装依赖
conan install . --build=missing

# 更新conanfile.txt添加新依赖
# 然后重新运行安装命令
```

### 使用vcpkg管理依赖

```bash
# 安装包
vcpkg install spdlog catch2 boost

# 在CMakeLists.txt中集成vcpkg
# set(CMAKE_TOOLCHAIN_FILE "/path/to/vcpkg/scripts/buildsystems/vcpkg.cmake")
```

## 使用指南

### 1. 项目初始化示例

```cpp
// src/main.cpp
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <spdlog/spdlog.h>
#include <fmt/format.h>

#include "core/application.h"

int main(int argc, char *argv[])
{
    // 初始化日志
    spdlog::info("Starting application");
    
    // 创建应用实例
    auto app = std::make_unique<Application>();
    
    spdlog::info("Application started successfully");
    
    // 应用程序逻辑
    return 0;
}
```

### 2. CMakeLists.txt 示例

```cmake
cmake_minimum_required(VERSION 4.0)

project(MyCppApp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置输出目录
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 如果使用Conan
# include(${CMAKE_BINARY_DIR}/conanbuild.cmake)

# 如果使用vcpkg
# find_package(spdlog CONFIG REQUIRED)

# 添加可执行文件
add_executable(${PROJECT_NAME})

# 设置源文件
target_sources(${PROJECT_NAME} PRIVATE
    src/main.cpp
    src/core/application.cpp
    src/utils/logger.cpp
)

# 设置头文件目录
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# 链接其他库（根据实际需求）
# target_link_libraries(${PROJECT_NAME} PRIVATE
#     spdlog::spdlog
#     fmt::fmt
# )

# 设置编译选项
if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE
        /W4
    )
else()
    target_compile_options(${PROJECT_NAME} PRIVATE
        -Wall -Wextra -pedantic
    )
endif()
```

### 3. Conan配置示例

```txt
# conanfile.txt
[requires]
spdlog/1.12.0@
fmt/10.1.1@
catch2/3.4.0@
boost/1.83.0@

[generators]
CMakeDeps
CMakeToolchain

[options]

[imports]
bin, *.dll -> ./bin # Copies DLLs to bin folder
lib, *.dylib* -> ./bin # Copies dylibs to bin folder
```

### 4. 测试示例

```cpp
// src/tests/test_main.cpp
#define CATCH_CONFIG_MAIN
#include <catch2/catch.hpp>

// src/tests/test_core.cpp
#include <catch2/catch.hpp>
#include "../core/application.h"

TEST_CASE("Application initialization", "[application]") {
    SECTION("Default constructor") {
        Application app;
        REQUIRE(app.getName().empty());
    }
    
    SECTION("Constructor with name") {
        Application app("TestApp");
        REQUIRE(app.getName() == "TestApp");
    }
}
```

## 最佳实践

### 1. 代码组织
1. **模块化设计**: 将功能划分为独立的模块
2. **头文件保护**: 使用#include guards或#pragma once
3. **命名空间**: 合理使用命名空间避免名称冲突
4. **RAII原则**: 使用资源获取即初始化原则

### 2. 构建系统最佳实践
1. **CMake预设**: 使用CMakePresets.json标准化构建配置
2. **依赖管理**: 使用Conan或vcpkg管理第三方库
3. **交叉编译**: 配置工具链文件支持不同平台
4. **构建类型**: 正确设置Debug/Release/RelWithDebInfo等构建类型

### 3. 跨平台开发
1. **条件编译**: 使用#ifdef处理平台特定代码
2. **路径处理**: 使用std::filesystem或Boost.Filesystem处理文件路径
3. **字符编码**: 统一使用UTF-8编码
4. **线程安全**: 注意跨平台的线程安全问题

### 4. 性能优化
1. **内存管理**: 合理使用智能指针
2. **容器选择**: 根据使用场景选择合适的STL容器
3. **算法优化**: 使用STL算法而非手写循环
4. **编译优化**: 启用编译器优化选项

### 5. 代码质量
1. **静态分析**: 使用Clang Static Analyzer或PVS-Studio
2. **代码格式化**: 使用clang-format保持代码风格一致
3. **代码审查**: 实施同行评审流程
4. **持续集成**: 配置CI/CD流水线

## 部署策略

### 1. 打包方式
- **Windows**: 使用NSIS或WiX Toolset
- **Linux**: 创建AppImage、Flatpak或传统包管理器包
- **macOS**: 创建DMG安装包或使用pkg打包

### 2. 依赖管理
- **静态链接**: 将依赖库静态链接到可执行文件
- **动态链接**: 打包所需的动态库文件
- **运行时检测**: 确保目标系统有必要的运行时库

### 3. 自动化部署
- **构建脚本**: 创建跨平台的构建和部署脚本
- **版本管理**: 使用语义化版本控制
- **发布流程**: 自动化测试、构建、签名和发布

## 扩展指南

### 添加新功能模块
1. 在src目录下创建新模块目录
2. 编写头文件和实现文件
3. 在CMakeLists.txt中添加源文件
4. 编写单元测试
5. 更新文档

### 集成新第三方库
1. 通过Conan或vcpkg添加依赖
2. 在CMakeLists.txt中链接库
3. 包含必要的头文件
4. 验证跨平台兼容性
5. 更新依赖配置文件

### 国际化支持
1. 使用标准库的locale设施
2. 创建翻译资源文件
3. 在应用中加载相应语言资源

这个技术栈为现代C++跨平台开发提供了全面的解决方案，涵盖了从开发到部署的整个生命周期，确保了高性能、跨平台兼容和可维护的桌面应用程序。