在实证研究中, 为了证明应用层的时延是占据主要部分的实验

分别搜集4个指标即可



# package loading
冷启动时延, 进行插桩即可
pod中执行 find /home/app -type d -name "__pycache__" -exec rm -rf {} +  模拟冷启动

743.199324 冷启动
434.108498 热启动

# pod instance  init 
命令 sudo journalctl -u containerd -f 观察特定 pod
创建 Pod 沙盒 (RunPodSandbox): 为 Pod 创建网络命名空间等基础环境。  0.527s 
拉取镜像 (PullImage): 从镜像仓库拉取函数镜像。 0.344s
创建容器 (CreateContainer): 在沙盒内，使用镜像创建容器的文件系统。 0.336s
启动容器 (StartContainer): 运行容器内的入口进程（即 Python 解释器）。 0.191s


863ms 是527+336 创建Pod的时间加上创建容器的时间
得到的图中的41% 是 (434+309) / (434+309+191+863) = 

+ 创建pod msg="RunPodSandbox for

```
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.030699020+08:00" level=info msg="StopContainer for \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" with timeout 2 (s)"
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.031154317+08:00" level=info msg="Stop container \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" with signal terminated"
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.431315778+08:00" level=info msg="RunPodSandbox for &PodSandboxMetadata{Name:heavy-py-774b94b947-pvgfv,Uid:0d484dd7-f2b1-406e-95f9-cd14626c4762,Namespace:openfaas-fn,Attempt:0,}"
Jul 10 17:02:21 cloud-node containerd[79222]: map[string]interface {}{"cniVersion":"0.3.1", "hairpinMode":true, "ipMasq":false, "ipam":map[string]interface {}{"ranges":[][]map[string]interface {}{[]map[string]interface {}{map[string]interface {}{"subnet":"10.244.0.0/24"}}}, "routes":[]types.Route{types.Route{Dst:net.IPNet{IP:net.IP{0xa, 0xf4, 0x0, 0x0}, Mask:net.IPMask{0xff, 0xff, 0x0, 0x0}}, GW:net.IP(nil), MTU:0, AdvMSS:0, Priority:0, Table:(*int)(nil), Scope:(*int)(nil)}}, "type":"host-local"}, "isDefaultGateway":true, "isGateway":true, "mtu":(*uint)(0xc000010800), "name":"cbr0", "type":"bridge"}
Jul 10 17:02:21 cloud-node containerd[79222]: delegateAdd: netconf sent to delegate plugin:
Jul 10 17:02:21 cloud-node containerd[79222]: {"cniVersion":"0.3.1","hairpinMode":true,"ipMasq":false,"ipam":{"ranges":[[{"subnet":"10.244.0.0/24"}]],"routes":[{"dst":"10.244.0.0/16"}],"type":"host-local"},"isDefaultGateway":true,"isGateway":true,"mtu":1450,"name":"cbr0","type":"bridge"}time="2025-07-10T17:02:21.821752476+08:00" level=info msg="loading plugin \"io.containerd.event.v1.publisher\"..." runtime=io.containerd.runc.v2 type=io.containerd.event.v1
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.821956136+08:00" level=info msg="loading plugin \"io.containerd.internal.v1.shutdown\"..." runtime=io.containerd.runc.v2 type=io.containerd.internal.v1
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.821977882+08:00" level=info msg="loading plugin \"io.containerd.ttrpc.v1.task\"..." runtime=io.containerd.runc.v2 type=io.containerd.ttrpc.v1
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.822230813+08:00" level=info msg="starting signal loop" namespace=k8s.io path=/run/containerd/io.containerd.runtime.v2.task/k8s.io/79abc1e1ca89ae284e0da7d53cf0de68292b54a9e58653b4ceb09163b7072134 pid=94422 runtime=io.containerd.runc.v2
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.958701465+08:00" level=info msg="RunPodSandbox for &PodSandboxMetadata{Name:heavy-py-774b94b947-pvgfv,Uid:0d484dd7-f2b1-406e-95f9-cd14626c4762,Namespace:openfaas-fn,Attempt:0,} returns sandbox id \"79abc1e1ca89ae284e0da7d53cf0de68292b54a9e58653b4ceb09163b7072134\""
Jul 10 17:02:21 cloud-node containerd[79222]: time="2025-07-10T17:02:21.960429972+08:00" level=info msg="PullImage \"localhost:5001/heavy-py:latest\""
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.235463911+08:00" level=info msg="ImageUpdate event &ImageUpdate{Name:localhost:5001/heavy-py:latest,Labels:map[string]string{io.cri-containerd.image: managed,},XXX_unrecognized:[],}"
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.268718599+08:00" level=info msg="ImageUpdate event &ImageUpdate{Name:sha256:1646ffaeebf091cabe0897fe82dbe7963c9f7892cc3fe2030bd29f0c9a90c851,Labels:map[string]string{io.cri-containerd.image: managed,},XXX_unrecognized:[],}"
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.285427955+08:00" level=info msg="ImageUpdate event &ImageUpdate{Name:localhost:5001/heavy-py:latest,Labels:map[string]string{io.cri-containerd.image: managed,},XXX_unrecognized:[],}"
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.302053978+08:00" level=info msg="ImageUpdate event &ImageUpdate{Name:localhost:5001/heavy-py@sha256:53e195f8f8c16dac19b5c48d577cb24974cb6844639b57a6ce23148c1f85eb87,Labels:map[string]string{io.cri-containerd.image: managed,},XXX_unrecognized:[],}"
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.304637878+08:00" level=info msg="PullImage \"localhost:5001/heavy-py:latest\" returns image reference \"sha256:1646ffaeebf091cabe0897fe82dbe7963c9f7892cc3fe2030bd29f0c9a90c851\""
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.312226326+08:00" level=info msg="CreateContainer within sandbox \"79abc1e1ca89ae284e0da7d53cf0de68292b54a9e58653b4ceb09163b7072134\" for container &ContainerMetadata{Name:heavy-py,Attempt:0,}"
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.648582667+08:00" level=info msg="CreateContainer within sandbox \"79abc1e1ca89ae284e0da7d53cf0de68292b54a9e58653b4ceb09163b7072134\" for &ContainerMetadata{Name:heavy-py,Attempt:0,} returns container id \"4e7e9ddbff07f54a1decc692ece641d4d914d9b5c3710c5dd429950567352df8\""
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.649445856+08:00" level=info msg="StartContainer for \"4e7e9ddbff07f54a1decc692ece641d4d914d9b5c3710c5dd429950567352df8\""
Jul 10 17:02:22 cloud-node containerd[79222]: time="2025-07-10T17:02:22.840506923+08:00" level=info msg="StartContainer for \"4e7e9ddbff07f54a1decc692ece641d4d914d9b5c3710c5dd429950567352df8\" returns successfully"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.042400429+08:00" level=info msg="Kill container \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\""
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.166218513+08:00" level=info msg="shim disconnected" id=7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.166349839+08:00" level=warning msg="cleaning up after shim disconnected" id=7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c namespace=k8s.io
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.166378066+08:00" level=info msg="cleaning up dead shim"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.188282672+08:00" level=warning msg="cleanup warnings time=\"2025-07-10T17:02:23+08:00\" level=info msg=\"starting signal loop\" namespace=k8s.io pid=94566 runtime=io.containerd.runc.v2\n"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.215473798+08:00" level=info msg="StopContainer for \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" returns successfully"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.216118838+08:00" level=info msg="StopPodSandbox for \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\""
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.216220547+08:00" level=info msg="Container to stop \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" must be in running or unknown state, current state \"CONTAINER_EXITED\""
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.290606054+08:00" level=info msg="shim disconnected" id=33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.290711818+08:00" level=warning msg="cleaning up after shim disconnected" id=33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3 namespace=k8s.io
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.290749944+08:00" level=info msg="cleaning up dead shim"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.309008825+08:00" level=warning msg="cleanup warnings time=\"2025-07-10T17:02:23+08:00\" level=info msg=\"starting signal loop\" namespace=k8s.io pid=94602 runtime=io.containerd.runc.v2\n"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.372328543+08:00" level=info msg="TearDown network for sandbox \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\" successfully"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.372412822+08:00" level=info msg="StopPodSandbox for \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\" returns successfully"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.966666444+08:00" level=info msg="StopPodSandbox for \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\""
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.966779860+08:00" level=info msg="Container to stop \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" must be in running or unknown state, current state \"CONTAINER_EXITED\""
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.968014995+08:00" level=info msg="RemoveContainer for \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\""
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.988147195+08:00" level=info msg="TearDown network for sandbox \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\" successfully"
Jul 10 17:02:23 cloud-node containerd[79222]: time="2025-07-10T17:02:23.988222688+08:00" level=info msg="StopPodSandbox for \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\" returns successfully"
Jul 10 17:02:24 cloud-node containerd[79222]: time="2025-07-10T17:02:24.095394608+08:00" level=info msg="RemoveContainer for \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" returns successfully"
Jul 10 17:02:24 cloud-node containerd[79222]: time="2025-07-10T17:02:24.096063291+08:00" level=error msg="ContainerStatus for \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\" failed" error="rpc error: code = NotFound desc = an error occurred when try to find container \"7a51f23cfc9d1506712d820fadb083018a7655038f3274f3c503547b3de8713c\": not found"
Jul 10 17:02:24 cloud-node containerd[79222]: time="2025-07-10T17:02:24.970901698+08:00" level=info msg="StopPodSandbox for \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\""
Jul 10 17:02:24 cloud-node containerd[79222]: time="2025-07-10T17:02:24.985933906+08:00" level=info msg="TearDown network for sandbox \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\" successfully"
Jul 10 17:02:24 cloud-node containerd[79222]: time="2025-07-10T17:02:24.985989142+08:00" level=info msg="StopPodSandbox for \"33e8ce084a3aac2e5d5e7423b4a39d8369dbd7acfd117e73238d4960fb5ab1d3\" returns successfully"
```