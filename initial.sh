sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

sudo apt-get update

sudo apt-get --assume-yes install ros-kinetic-desktop-full

sudo apt-get --assume-yes install ros-kinetic-turtlebot3-*

echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc

echo "export TURTLEBOT3_MODEL='burger'" >> ~/.bashrc

echo "export SVGA_VGPU10=0" >> ~/.bashrc

source ~/.bashrc



