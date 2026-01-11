$reg_name = "kind-registry"
$reg_port = "5001"
$running = docker inspect -f '{{.State.Running}}' $reg_name 2>$null

if ($running -ne "true") {
    Write-Host "Creating registry container..."
    docker run -d --restart=always -p "127.0.0.1:${reg_port}:5000" --name $reg_name registry:2
} else {
    Write-Host "Registry already running."
}

Write-Host "Creating Kind cluster..."
kind create cluster --config kind-config.yaml --name cloudops-k8s

Write-Host "Connecting registry to kind network..."
docker network connect "kind" $reg_name 2>$null

Write-Host "Documenting registry usage in ConfigMap..."
$configMap = @"
apiVersion: v1
kind: ConfigMap
metadata:
  name: local-registry-hosting
  namespace: kube-public
data:
  localRegistryHosting.v1: |
    host: "localhost:${reg_port}"
    help: "https://kind.sigs.k8s.io/docs/user/local-registry/"
"@

$configMap | kubectl apply -f -
