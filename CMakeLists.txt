cmake_minimum_required(VERSION 3.15...3.26)

project(
  ${SKBUILD_PROJECT_NAME}
  LANGUAGES C
  VERSION ${SKBUILD_PROJECT_VERSION})

# ExternalProject for ISA-L
include(ExternalProject)
set(ISAL_SOURCE_DIR "${CMAKE_SOURCE_DIR}/src/asammdf/blocks/isa-l")
if (WIN32)
  set(ISAL_MAKE_CMD nmake /f Makefile.nmake)
  set(ISAL_STATIC_LIB ${ISAL_SOURCE_DIR}/isa-l.lib)
else()
  set(ISAL_CFG_CMD ./autogen.sh && ./configure --enable-shared=no CFLAGS=-fPIC)
  set(ISAL_MAKE_CMD make)
  set(ISAL_STATIC_LIB ${ISAL_SOURCE_DIR}/.libs/libisal.a)
endif()
ExternalProject_Add(isal_ext_prj
    SOURCE_DIR ${ISAL_SOURCE_DIR}
    CONFIGURE_COMMAND ${ISAL_CFG_CMD}
    BUILD_COMMAND ${ISAL_MAKE_CMD}
    INSTALL_COMMAND ""  # No install step needed
    BUILD_BYPRODUCTS ${ISAL_STATIC_LIB}
    BUILD_IN_SOURCE 1   # Build within the source tree
)

# Define the ISA-L static library
add_library(isal STATIC IMPORTED)
set_target_properties(isal PROPERTIES IMPORTED_LOCATION ${ISAL_STATIC_LIB})
include_directories(${ISAL_SOURCE_DIR}/include)

find_package(
  Python
  COMPONENTS
  Interpreter
  Development.Module
  ${SKBUILD_SABI_COMPONENT}
  NumPy
  REQUIRED)

python_add_library(cutils
                   MODULE
                   src/asammdf/blocks/cutils.c
                   src/asammdf/blocks/miniz.c
                   src/asammdf/blocks/zlib_isal.c
                   WITH_SOABI USE_SABI 3.9)

# link libraries to cutils
target_link_libraries(cutils PRIVATE Python::NumPy)
target_link_libraries(cutils PRIVATE isal)

install(TARGETS cutils DESTINATION "asammdf/blocks")
