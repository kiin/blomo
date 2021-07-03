# BLOMO

### Balancing Load On My Own


Note: Create virtual interface
      sudo ip link add link eth0 address 00:11:11:11:11:11 virtual0 type macvlan
      sudo ifconfig virtual0 up
      sudo ifconfig eth0 promisc 
