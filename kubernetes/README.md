# CIAF Kubernetes Deployment Guide

This directory contains Kubernetes manifests and Helm charts for deploying CIAF in production environments.

## 📁 Directory Structure

```
kubernetes/
├── deployments/          # Deployment manifests (4 services)
│   ├── vault-deployment.yaml
│   ├── verification-deployment.yaml
│   ├── frontend-deployment.yaml
│   └── nginx-deployment.yaml
├── statefulsets/         # StatefulSet manifests (databases)
│   ├── postgresql-statefulset.yaml
│   └── redis-statefulset.yaml
├── services/             # Service manifests
│   ├── vault-service.yaml
│   ├── verification-service.yaml
│   ├── frontend-service.yaml
│   ├── postgresql-service.yaml
│   └── redis-service.yaml
├── configmaps/           # Configuration
│   ├── app-config.yaml
│   └── nginx-config.yaml
├── secrets/              # Secrets (templates - use Sealed Secrets in prod)
│   ├── db-credentials.yaml
│   └── api-keys.yaml
├── ingress/              # Ingress for external access
│   └── main-ingress.yaml
├── storage/              # Persistent storage
│   └── persistent-storage.yaml
├── rbac/                 # Role-based access control
│   ├── service-account.yaml
│   ├── role.yaml
│   └── role-binding.yaml
└── monitoring/           # Prometheus & Grafana
    ├── prometheus-configmap.yaml
    ├── grafana-deployment.yaml
    └── service-monitor.yaml

helm/ciaf-chart/         # Helm chart for simplified deployment
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── statefulset.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── serviceaccount.yaml
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3 (for Helm deployment)
- cert-manager (for TLS certificates)
- Ingress controller (nginx recommended)

### Option 1: Deploy with kubectl (Raw Manifests)

```bash
# Create namespace
kubectl create namespace ciaf

# Deploy in order:
# 1. RBAC
kubectl apply -f kubernetes/rbac/

# 2. ConfigMaps and Secrets
kubectl apply -f kubernetes/configmaps/
# Edit secrets first with actual values!
kubectl apply -f kubernetes/secrets/

# 3. Storage
kubectl apply -f kubernetes/storage/

# 4. StatefulSets (databases)
kubectl apply -f kubernetes/statefulsets/

# 5. Services
kubectl apply -f kubernetes/services/

# 6. Deployments (applications)
kubectl apply -f kubernetes/deployments/

# 7. Ingress
kubectl apply -f kubernetes/ingress/

# 8. Monitoring (optional)
kubectl apply -f kubernetes/monitoring/
```

### Option 2: Deploy with Helm (Recommended)

```bash
# Add custom values
cat > custom-values.yaml <<EOF
global:
  domain: your-domain.com

images:
  vault:
    repository: your-registry/ciaf-core
    tag: "v1.0.0"
  
postgresql:
  # Set password via --set-string rather than values file
  database: ciaf_proofs
  username: ciaf_verification

persistence:
  enabled: true
  storageClass: "fast-ssd"  # Adjust for your cloud provider

ingress:
  enabled: true
  hosts:
    - host: ciaf.your-domain.com
      paths:
        - path: /
          pathType: Prefix
EOF

# Install with Helm
helm install ciaf ./helm/ciaf-chart \
  -f custom-values.yaml \
  --set-string postgresql.password="$(openssl rand -base64 32)" \
  --set-string security.jwtSecret="$(openssl rand -hex 32)" \
  --set-string security.apiKeySecret="$(openssl rand -hex 32)" \
  --namespace ciaf \
  --create-namespace

# Check status
helm status ciaf -n ciaf
kubectl get pods -n ciaf
```

## 🔐 Security Configuration

### 1. Generate Secrets

```bash
# Generate strong secrets
export DB_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -hex 32)
export API_KEY_SECRET=$(openssl rand -hex 32)
export VAULT_MASTER_KEY=$(openssl rand -hex 32)

# Create secret
kubectl create secret generic ciaf-secrets \
  --from-literal=postgres_password="$DB_PASSWORD" \
  --from-literal=jwt_secret_key="$JWT_SECRET" \
  --from-literal=api_key_secret="$API_KEY_SECRET" \
  --from-literal=vault_master_key="$VAULT_MASTER_KEY" \
  --namespace ciaf \
  --dry-run=client -o yaml > ciaf-secrets.yaml

# For production, use Sealed Secrets
kubeseal < ciaf-secrets.yaml > ciaf-secrets-sealed.yaml
kubectl apply -f ciaf-secrets-sealed.yaml
```

### 2. TLS Certificates

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@your-domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## 📊 Monitoring

Access monitoring dashboards:

```bash
# Port-forward Grafana
kubectl port-forward -n ciaf svc/grafana 3000:3000

# Port-forward Prometheus
kubectl port-forward -n ciaf svc/prometheus 9090:9090
```

Default credentials:
- Grafana: admin / (jwt_secret_key from secrets)
- Prometheus: No authentication by default

## 🔧 Maintenance

### Scaling

```bash
# Scale vault instances
kubectl scale deployment ciaf-vault --replicas=5 -n ciaf

# With Helm
helm upgrade ciaf ./helm/ciaf-chart \
  --set replicaCount.vault=5 \
  --namespace ciaf
```

### Updates

```bash
# Update with kubectl
kubectl set image deployment/ciaf-vault \ciaf-core=ciaf-core:v1.1.0 -n ciaf

# Update with Helm
helm upgrade ciaf ./helm/ciaf-chart \
  --set images.vault.tag=v1.1.0 \
  --namespace ciaf
```

### Backup PostgreSQL

```bash
# Create backup
kubectl exec -n ciaf ciaf-postgresql-0 -- \
  pg_dump -U ciaf_verification ciaf_proofs > backup.sql

# Restore backup
kubectl exec -i -n ciaf ciaf-postgresql-0 -- \
  psql -U ciaf_verification ciaf_proofs < backup.sql
```

## 🔍 Troubleshooting

```bash
# Check pod status
kubectl get pods -n ciaf

# View logs
kubectl logs -f deployment/ciaf-vault -n ciaf

# Describe pod
kubectl describe pod <pod-name> -n ciaf

# Execute into pod
kubectl exec -it <pod-name> -n ciaf -- /bin/sh

# Check events
kubectl get events -n ciaf --sort-by='.lastTimestamp'
```

## 🌐 Cloud Provider Specific Notes

### AWS (EKS)

```bash
# Use gp3 storage class
storageClass: gp3

# Use AWS Load Balancer Controller
service.nginx.type: LoadBalancer
service.nginx.annotations:
  service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
```

### GCP (GKE)

```bash
# Use pd-ssd storage class
storageClass: pd-ssd

# GKE Ingress
ingress.className: "gce"
```

### Azure (AKS)

```bash
# Use managed-premium storage class
storageClass: managed-premium

# Azure Ingress
ingress.className: "azure/application-gateway"
```

## 📖 Additional Resources

- [CIAF Documentation](../../README.md)
- [Docker Compose Guide](../../DOCKER.md)
- [Local Setup](../../LOCAL_SETUP.md)
- [Frontend Guide](../../FRONTEND_GETTING_STARTED.md)

## 🆘 Support

For issues or questions:
- GitHub Issues: https://github.com/DenzilGreenwood/CIAF_Model_Creation/issues
- Documentation: [ROADMAP_TO_100_PERCENT.md](../../ROADMAP_TO_100_PERCENT.md)
