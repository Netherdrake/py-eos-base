# Creating a development environment
This guide supposes Ubuntu 16.04 LTS as a base OS.


## Installation
See the [Dockerfile](https://github.com/EOSIO/eos/blob/master/Docker/Dockerfile) for convenient installation.

This guide is for local setup, and is a bit more convoluted.
```
sudo su
```

Then:

```bash
#!/bin/bash

## LLVM
echo "deb http://apt.llvm.org/xenial/ llvm-toolchain-xenial-4.0 main" >> /etc/apt/sources.list.d/llvm.list
wget -O - http://apt.llvm.org/llvm-snapshot.gpg.key|sudo apt-key add -
apt update


## APT DEPENDENCIES
apt install -y git-core automake autoconf libtool build-essential pkg-config libtool \
               mpi-default-dev libicu-dev python-dev python3-dev libbz2-dev zlib1g-dev libssl-dev libgmp-dev \
               clang-4.0 lldb-4.0 lld-4.0


## CLANG DEFAULT
update-alternatives --install /usr/bin/clang clang /usr/lib/llvm-4.0/bin/clang 400
update-alternatives --install /usr/bin/clang++ clang++ /usr/lib/llvm-4.0/bin/clang++ 400


## CMAKE
cd /tmp && wget https://cmake.org/files/v3.9/cmake-3.9.0-Linux-x86_64.sh
mkdir /opt/cmake && chmod +x /tmp/cmake-3.9.0-Linux-x86_64.sh
sh /tmp/cmake-3.9.0-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
ln -s /opt/cmake/bin/cmake /usr/local/bin


## BOOST
cd /tmp && wget https://dl.bintray.com/boostorg/release/1.64.0/source/boost_1_64_0.tar.gz
tar zxf boost_1_64_0.tar.gz
cd boost_1_64_0
./bootstrap.sh --with-toolset=clang
./b2 -a -j$(nproc) stage release -sHAVE_ICU=1 --sICU_PATH=/usr
./b2 install --prefix=/usr


## SECP256k1
cd /tmp && git clone https://github.com/cryptonomex/secp256k1-zkp.git
cd secp256k1-zkp
./autogen.sh && ./configure && make && make install
ldconfig && rm -rf /tmp/secp256k1-zkp*


## WASM
cd /tmp && mkdir -p wasm-compiler && cd wasm-compiler
git clone --depth 1 --single-branch --branch release_40 https://github.com/llvm-mirror/llvm.git
cd llvm/tools && git clone --depth 1 --single-branch --branch release_40 https://github.com/llvm-mirror/clang.git
cd .. && mkdir build && cd build
cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX=/opt/wasm -DLLVM_TARGETS_TO_BUILD= -DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=WebAssembly -DCMAKE_BUILD_TYPE=Release ../
make -j$(nproc) install && rm -rf /tmp/wasm-compiler


echo "All done."

```

## CLion Config
Configure cmake in CLION: `File > Settings > Build,Execution,Deployment > CMake`

### CMake Options
```
-DCMAKE_CXX_COMPILER=clang++
-DCMAKE_C_COMPILER=clang
```

### Environment
WASM_LLVM_CONFIG=/opt/wasm/bin/llvm-config


## Building
After building with Clion, run:
```
cd cmake-build-debug
sudo make install
```

This will install eos in `/usr/local/bin/eosd`.

## Run

Using stock config (now includes rpc).
```
eosd --genesis-json /home/user/Github/eos/genesis.json --config /home/user/Github/eos/Docker/config.ini
```

Plugins and other properties can also be initialized trough flags.
```
# eosd --genesis-json /home/user/Github/eos/genesis.json --plugin eos::producer_plugin eos::chain_api_plugin eos::http_plugin
```



### Updating EOS
Compiling eos, inside of /home/user/Github/eos:
```bash
#!/bin/bash
cd /home/user/Github/eos
git pull
git submodule update --recursive --remote
rm -rf build
mkdir -p build && cd build
WASM_LLVM_CONFIG=/opt/wasm/bin/llvm-config cmake -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang -DCMAKE_INSTALL_PREFIX=/opt/eos ..
make -j$(nproc)
sudo make install
```
