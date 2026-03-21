# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file LICENSE.rst or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "/Users/doyungu/Developer/pico-sdk/tools/pioasm")
  file(MAKE_DIRECTORY "/Users/doyungu/Developer/pico-sdk/tools/pioasm")
endif()
file(MAKE_DIRECTORY
  "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pioasm"
  "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pioasm-install"
  "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/tmp"
  "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp"
  "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src"
  "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/Users/doyungu/Developer/hack-a-bot-2026/src/master-pico/c_sdk/build_pico/pico-sdk/src/rp2_common/pico_cyw43_driver/pioasm/src/pioasmBuild-stamp${cfgdir}") # cfgdir has leading slash
endif()
