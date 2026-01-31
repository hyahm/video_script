#!/bin/bash
###  编译报错过了话， 先 make clean
cd 
mkdir src
yum -y install epel-release make git gcc hg gcc-c++ bzip2 libchromaprint-devel  # rpm -ivh http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
cd src
wget http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz --no-check-certificate
tar -xf yasm-1.3.0.tar.gz
cd yasm-1.3.0
./configure
make -j 88
sudo make install


# cd ..
# wget https://downloads.xvid.com/downloads/xvidcore-1.3.7.tar.gz
# tar -xf xvidcore-1.3.7.tar.gz
# cd build/generic &&
# sed -i 's/^LN_S=@LN_S@/& -f -v/' platform.inc.in &&
# ./configure --prefix=/usr &&
# make
# sed -i '/libdir.*STATIC_LIB/ s/^/#/' Makefile &&
# make install && chmod -v 755 /usr/lib64/libxvidcore.so.4.3
# cd ../..

cd ..
rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
wget https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/nasm-2.14.02.tar.bz2 --no-check-certificate
tar -xf nasm-2.14.02.tar.bz2
cd nasm-2.14.02/
./configure && make -j 88  
sudo make install

cd ..
git clone https://github.com/mirror/x264.git
cd x264
./configure --enable-shared && make -j 88 
sudo make install

cd ..
wget  http://downloads.webmproject.org/releases/webp/libwebp-1.1.0.tar.gz --no-check-certificate
tar -xf libwebp-1.1.0.tar.gz
cd libwebp-1.1.0
./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux --enable-libwebpdecoder --enable-libwebpextras --enable-swap-16bit-csp --disable-static 
make -j 88 
sudo make install

# fedora
# cd ..
# hg clone http://hg.videolan.org/x265
# cd x265
# cd build/linux
# ./make-Makefiles.bash
# make && make install
# cd ../..



cd ..
wget https://nchc.dl.sourceforge.net/project/opencore-amr/opencore-amr/opencore-amr-0.1.3.tar.gz --no-check-certificate
tar -xf opencore-amr-0.1.3.tar.gz
cd opencore-amr-0.1.3
./configure && make && sudo make install

# sudo yum install tcl pkgconfig openssl-devel cmake gcc gcc-c++ make automake
# cd ..
# git clone https://github.com/Haivision/srt.git
# cd srt


cd ..
git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
cd nv-codec-headers
make
sudo make install

cd ..
wget https://ffmpeg.org/releases/ffmpeg-4.2.2.tar.bz2 --no-check-certificate
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:/usr/lib64/pkgconfig:/usr/share/pkgconfig:/usr/lib/pkgconfig:/usr/local/lib64/pkgconfig
yum -y install  frei0r-devel ladspa-devel libass-devel libbluray-devel libbs2b-devel libxml2-devel libcaca-devel libtheora-devel twolame-devel libvorbis-devel wavpack-devel zvbi-devel libchromaprint-devel x265-devel
yum -y install libdc1394-devel opencv-devel openjpeg-devel librsvg2-devel soxr-devel speex-devel rubberband-devel xvidcore-devel cppzmq-devel openal-soft-devel SDL2-devel openjpeg2-devel lilv-devel codec2-devel libssh-devel gsm-devel
yum -y install gmp-devel gnutls-devel aom libdav1d-devel libmfx-devel libmysofa-devel opus-devel  libopenmpt-devel
yum -y install snappy-devel vo-amrwbenc-devel zimg-devel frei0r-devel opencore-amr-devel

#   yum -y install libdc1394-devel opencv-devel openjpeg-devel librsvg2-devel soxr-devel speex-devel rubberband-devel xvidcore-devel cppzmq-devel openal-soft-devel SDL2-devel openjpeg2-devel lilv-devel codec2-devel libssh-devel gsm-devel
# sudo apt -y install libchromaprint-dev frei0r-plugins-dev  ladspa-sdk liblilv-dev libass-dev libbluray-dev librsvg2-dev
# sudo apt -y install libbs2b-dev libcaca-dev libcodec2-dev libdc1394-dev libdrm-dev libgsm1-dev libopenjp2-7-dev librubberband-dev
# sudo apt -y install libsoxr-dev libssh-dev libspeex-dev libtheora-dev libtwolame-dev libvorbis-dev libwavpack-dev
# sudo apt -y install libx265-dev libxvidcore-dev libzmq3-dev libzvbi-dev libopenal-dev libgl1-mesa-dev libsdl2-dev
tar -xf ffmpeg-4.2.2.tar.bz2
cd ffmpeg-4.2.2
./configure --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --arch=amd64 --enable-libopenmpt  --enable-nvdec --enable-nvenc --enable-cuvid --enable-ffnvcodec --enable-libmysofa --enable-libvo-amrwbenc --enable-gmp --enable-zlib --enable-lzma --enable-libzimg  --enable-libsnappy  --enable-libopencore-amrwb --enable-libopencore-amrnb --enable-libdav1d --enable-iconv --enable-version3 --enable-gpl --enable-fontconfig --disable-stripping --disable-filter=resample --enable-avisynth --enable-ladspa --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcodec2 --enable-libfontconfig --enable-libfreetype --enable-librubberband --enable-libfribidi --enable-libgsm --enable-libopenjpeg --enable-librsvg --enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvorbis --enable-libwavpack --enable-libwebp --enable-libx265 --enable-libxml2 --enable-libxvid --enable-libzmq --enable-libzvbi --enable-lv2 --enable-openal --enable-opengl --enable-sdl2 --enable-libdc1394 --enable-libdrm --enable-chromaprint --enable-frei0r --enable-libx264 --enable-shared --extra-cflags=-I/usr/local/include --extra-ldflags=-L/usr/local/lib --enable-libxcb --enable-openssl  --enable-nonfree

make -j 88
sudo make install
sudo /bin/cp -f /usr/lib/x86_64-linux-gnu/* /usr/lib64/
sudo /bin/cp -f /usr/local/lib/libx264.so.* /usr/lib64/
cp /opencore-amr-0.1.3/amrnb/.libs/libopencore-amrnb.so.0 /usr/lib64/
cp /usr/local/lib/libopencore-amrwb.so.0 /usr/lib64/
cp /usr/local/lib/libopencore-amrnb.so.0 /usr/lib64/

