# IFLOW Context File - ckpttnpy

## 项目概述

这是一个名为ckpttnpy的Python项目，专门用于电路分区算法的实现。该项目主要实现了多级分区算法，用于将复杂的超图（hypergraph）分割成多个部分，同时保持特定的平衡和优化标准。主要算法基于Fiduccia-Mattheyses（FM）分区方法，支持二分和K路分区。

## 核心组件

- **MLPartMgr.py**: 主要的多级分区管理器，包含核心算法逻辑
- **FMPartMgr.py**: Fiduccia-Mattheyses分区管理器，用于分区状态的快照和恢复
- **FMBiGainCalc.py**: 二分图增益计算器，用于计算分区移动的增益
- **其他文件**: 包含不同类型的增益管理器、约束管理器等辅助组件

## 依赖关系

- `networkx`: 用于图结构的表示和操作
- `luk036/mywheel`: 自定义工具库
- `luk036/netlistx`: 网表处理库
- 其他测试和开发依赖（如pytest, coverage等）

## 构建和运行

### 安装依赖
```bash
pip3 install git+https://github.com/luk036/mywheel.git
pip3 install git+https://github.com/luk036/netlistx.git
pip3 install -r ./requirements.txt
python3 setup.py develop
```

### 运行测试
```bash
python3 setup.py test
```

## 项目架构

- **源代码**: `/src/ckpttnpy/`
- **测试**: `/tests/`
- **文档**: `/docs/`
- **实验**: `/experiments/`
- **配置文件**: `setup.py`, `setup.cfg`, `pyproject.toml`, `requirements/`

## 开发约定

- 项目使用PyScaffold 4.5构建
- 代码遵循Python标准实践
- 测试使用pytest框架
- 项目使用semantic versioning

## 算法说明

该项目实现的算法主要用于电路设计中的分区问题，核心算法是多级分区方法，包括图收缩、增益计算和优化等步骤。算法通过迭代改进分区，以最小化分区间的连接成本并满足平衡约束。