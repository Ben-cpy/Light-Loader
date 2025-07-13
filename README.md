# 🚀 LightLoader

**LightLoader** is a cutting-edge optimization framework that dramatically reduces OpenFaaS function cold start times through intelligent static analysis and lazy loading techniques. Achieve **up to 50% faster cold starts** with zero code changes required! ⚡

## 🎯 What is LightLoader?

LightLoader transforms your Python serverless functions by:
- 🔍 **Static Analysis**: Analyzing call graphs to identify unused dependencies
- ✂️ **Dead Code Elimination**: Removing unnecessary packages and functions
- 🔄 **Lazy Loading**: Converting imports to load only when needed
- 🏗️ **Template Integration**: Seamlessly integrating with OpenFaaS build process

## 🏃‍♂️ Quick Start

### Prerequisites
- OpenFaaS CLI installed
- Docker configured
- Kubernetes, we use 1.20.15 with containerd 1.6.25

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ben-cpy/LightLoader.git
   cd lightloader
   ```

2. **Optimize your OpenFaaS functions**:
   ```bash
   ./src/lightloader/modify.sh /path/to/your/openfaas/project
   ```

3. **Deploy optimized functions**:
   ```bash
   cd /path/to/your/openfaas/project
   faas-cli up -f your-function.yml
   ```

## 📁 Project Structure

```
lightloader/
├── 📁 src/lightloader/          # Core optimization engine
│   ├── Light.py                # Main orchestrator
│   ├── modify.sh              # OpenFaaS integration script
│   ├── lazy_load/             # Import transformation logic
│   └── remove_option/         # Dead code elimination
├── 📁 tools/                   # Static analysis tools
│   ├── pycg/                  # alternative call graph maker
│   └── jarvis/                #  generate call graph
├── 📁 tests/                   # Test suite and experiments
│   ├── empirical_study_case/  # Test function cases for validation
│   ├── openfaas/              # Sample OpenFaaS functions for testing
│   └── experiments/           # Performance measurement scripts
├── 📁 empirical_study/         # Research analysis scripts for paper validation
│   ├── container_init_time/   # Container startup analysis
│   ├── py_large_latency/      # Large module impact studies
│   └── ...                    # Other empirical study scripts
├── 📁 call_graph_repo/         # Pre-computed call graphs for OpenFaaS functions
└── 📁 experiments/             # Experimental testing scripts
```

## 🔧 How It Works

### 1. Static Analysis Pipeline
```bash
# Generate call graph for your function
cd tools/Jarvis
python  jarvis_cli.py /home/path/your-app/handler.py --package /your/local/project/path --decy  --precision  -o call_graph.json
```
you could use the pre-computed cases by us in ./call_graph_repo

### 2. Pull Template and Create a Function
you can see a ./template file create in your current folder.
```bash
faas-cli new --lang python3-debian  --prefix=yourname hello-python
```

### 3. Optimization Process
The system runs an 8-step pipeline:
1. **Reduce optional files** - Remove non-essential files
2. **Find magic functions** - Identify dynamically loaded code
3. **Analyze used functions** - Build dependency graph
4. **Identify used packages** - Determine actual requirements
5. **Lazy load packages** - Transform imports to function scope
6. **Rewrite code** - Generate optimized handler
7. **Update template** - Integrate with OpenFaaS build
8. **Deploy** - Launch optimized function

you can get a optimized python template that achieve these optimziation
```bash
./src/lightloader/modify.sh /path/to/your/openfaas/project
```

### 4. Deploy

```bash
faas-cli up -f ./hello-python.yml
```


## 🧪 Testing & Validation

### Run Tests
these are OpenFaaS function used in our expeirments and empirical study
```bash
# Test function cases for validation
cd tests/empirical_study_case  # Research validation test cases

# Sample OpenFaaS functions for testing  
cd tests/openfaas              # Real OpenFaaS function examples
```

