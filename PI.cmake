set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_VERSION 1)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(tools <absolute path to toolchain directory, for e.g $ENV{HOME}/rpi_rootfs/tools/cross-pi-gcc-10.2.0-1>) # warning change toolchain path here.
set(rootfs_dir ${SYSROOT}/rootfs>) # warning change compiled rootfs path here.

set(CMAKE_FIND_ROOT_PATH ${rootfs_dir})
set(CMAKE_SYSROOT ${rootfs_dir})

#linker flags
set(CMAKE_LIBRARY_ARCHITECTURE arm-linux-gnueabihf)
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fPIC -Wl,-rpath-link,${CMAKE_SYSROOT}/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE} -L${CMAKE_SYSROOT}/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE}")
set(CMAKE_C_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -Wl,-rpath-link,${CMAKE_SYSROOT}/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE} -L${CMAKE_SYSROOT}/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -Wl,-rpath-link,${CMAKE_SYSROOT}/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE} -L${CMAKE_SYSROOT}/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE}")

## Compiler Binary 
set(BIN_PREFIX ${tools}/bin/arm-linux-gnueabihf)

set(CMAKE_C_COMPILER ${BIN_PREFIX}-gcc)
set(CMAKE_CXX_COMPILER ${BIN_PREFIX}-g++ )
set(CMAKE_LINKER ${BIN_PREFIX}-ld CACHE STRING "Set the cross-compiler tool LD" FORCE)
set(CMAKE_AR ${BIN_PREFIX}-ar CACHE STRING "Set the cross-compiler tool AR" FORCE)
set(CMAKE_NM {BIN_PREFIX}-nm CACHE STRING "Set the cross-compiler tool NM" FORCE)
SET(CMAKE_OBJCOPY ${BIN_PREFIX}-objcopy CACHE STRING "Set the cross-compiler tool OBJCOPY" FORCE)
set(CMAKE_OBJDUMP ${BIN_PREFIX}-objdump CACHE STRING "Set the cross-compiler tool OBJDUMP" FORCE)
set(CMAKE_RANLIB ${BIN_PREFIX}-ranlib CACHE STRING "Set the cross-compiler tool RANLIB" FORCE)
set(CMAKE_STRIP ${BIN_PREFIX}-strip CACHE STRING "Set the cross-compiler tool STRIP" FORCE)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
