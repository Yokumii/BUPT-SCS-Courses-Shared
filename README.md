<div align="center">
  <h1>BUPT-SCS-Courses-Shared</h1>
  <p>
    <img src="https://img.shields.io/github/stars/Yokumii/BUPT-SCS-Courses-Shared?style=social" alt="stars">
    <img src="https://img.shields.io/github/forks/Yokumii/BUPT-SCS-Courses-Shared?style=social" alt="forks">
  </p>
</div>

本仓库收录了个人在巴普特（北京邮电大学）括号院（计算机学院）相关课程的学习资料，内容涵盖课件、考试资料、个人实验报告及代码和课程设计等，旨在为同学们的学习提供参考☝️。**使用请遵循学术诚信规范，产生的一切不当后果与作者无关**。

> 如果需要补充或纠正资料，欢迎提交ISSUE、PR或通过邮件联系！ 

> 不同年级当年培养方案**不太相同**，存在某些课程**不在本年级**培养方案中，以培养方案为准。2023级的培养方案请参考[培养方案](./Additional-Information/Cultivation/计算机学院（国家示范性软件学院）2023级本科专业培养方案-0831.pdf)

---

## 食用指南

仓库体积较大，无需完整克隆。使用 Git 部分克隆即可只下载需要的课程：

```bash
# 仅克隆元数据，不下载文件（推荐）
git clone --filter=blob:none --no-checkout https://github.com/Yokumii/BUPT-SCS-Courses-Shared.git
cd BUPT-SCS-Courses-Shared

# 仅检出所需课程，例如操作系统和数据库
git sparse-checkout set Term5/Operating-System Term5/DataBase-System-Concepts
git checkout
```

> `--filter=blob:none` 会延迟下载文件内容，仅在 `git checkout` 时才按需拉取所需文件，大幅减少下载量。

## 资料列表

### 第一学期

| 课程名称       | 课程性质      | 课程学分 | 作业/实验                                               | 期末考核 |
| -------------- | ------------- | -------- | ------------------------------------------------------- | -------- |
| [创新创业实践课](./Term1/Innovation-and-Entrepreneurship-Practice) | 指选 | 1.5      | [大数据技术模块](./Term1/Innovation-and-Entrepreneurship-Practice/Big-Data-Technology)<br>[移动应用开发模块](./Term1/Innovation-and-Entrepreneurship-Practice/Mobile-App-Development) | 按实验验收和报告给分 |

### 第二学期

| 课程名称       | 课程性质      | 课程学分 | 作业/实验                                               | 期末考核 |
| -------------- | ------------- | -------- | ------------------------------------------------------- | -------- |
| [大学物理C](./Term2/College-Physics-C) | 必修 | 4      | 章节作业 | 期中 + 期末考试 |
| [电子电路分析基础](./Term2/Electronic-Circuit-Analysis) | 必修 | 2 | 章节作业<br>[平时作业答案](./Term2/Electronic-Circuit-Analysis) | 期中 + 期末考试 |
| [离散数学 (上)](./Term2/Discrete-Mathematics-I) | 必修 | 2 | 章节作业<br>[平时作业答案](./Term2/Discrete-Mathematics-I/Homeworks) | 期中 + 期末考试<br>[往年题](./Term2/Discrete-Mathematics-I/Past-Exams) |
| [计算导论与程序设计课程设计](https://github.com/Yokumii/BUPT-SCS-McDonalds-Ordering-System) | 选修 | 1.5 | PTA OJ | 大作业<br>个人项目见[麦当劳点餐系统](https://github.com/Yokumii/BUPT-SCS-McDonalds-Ordering-System) |

### 第三学期

| 课程名称       | 课程性质      | 课程学分 | 作业/实验                                               | 期末考核 |
| -------------- | ------------- | -------- | ------------------------------------------------------- | -------- |
| [离散数学 (下)](Term3/Discrete-Mathematics-II) | 必修 | 3     | 章节作业 | 期中 + 期末考试 |
| [数字逻辑与数字系统](./Term3/Digital-Logic-and-Digital-Systems) | 必修 | 4 | [编程作业解答](./Term3/Digital-Logic-and-Digital-Systems/Homeworks)<br>[6 次实验报告](./Term3/Digital-Logic-and-Digital-Systems/Labs) | 期中 + 期末考试<br>[往年题](./Term3/Digital-Logic-and-Digital-Systems/Past-Exams) |
| [数据结构](./Term3/Data-Structure) | 必修 | 4 | PTA OJ<br>[3 次实验报告](./Term3/Data-Structure/Labs) | 期中 + 期末考试<br>[往年题](./Term3/Data-Structure/Past-Exams) |
| [概率论与数理统计](./Term3/Probability-Theory-and-Mathematical-Statistics) | 选修 | 4 | 平时作业 + 期中小论文 | 期末考试 |
| [计算机系统基础](./Term3/CSAPP) | 必修 | 2 + 0.5 | [个人课后作业](./Term3/CSAPP/Homeworks)<br>4 次实验 | 期中 + 期末考试<br>[往年题和回忆](./Term3/CSAPP/Past-Exams) |
| [马原](./Term3/Fundamentals-of-Marxism) | 必修 | 2.5 + 0.5 | 调查报告 | 期末考试<br>[一些复习资料](./Term3/Fundamentals-of-Marxism/Reviews) |
| [矩阵理论与方法](./Term3/Matrix-Theory-and-Methods) | 选修 | 2 | 平时作业<br>[个人代码](https://github.com/Yokumii/Codes-for-Matrix-Algebra) | 大论文 |

### 第四学期

| 课程名称       | 课程性质      | 课程学分 | 作业/实验                                               | 期末考核 |
| -------------- | ------------- | -------- | ------------------------------------------------------- | -------- |
| [计算机组成原理](./Term4/Computer-Organization) | 必修 | 4    | [章节作业答案](./Term4/Computer-Organization/Homeworks)<br>[6 次实验报告](./Term4/Computer-Organization/Labs) | 期中 + 期末考试<br>[往年题](./Term4/Computer-Organization/Past-Exams) |
| [计算机网络](./Term4/Computer-Networking) | 必修 | 4 | [章节作业答案](./Term4/Computer-Networking/Homeworks)<br>[实验一](https://github.com/Yokumii/BuptNetworkLab_Datelink)<br>[实验二](./Term4/Computer-Networking/Labs/Lab2) | 期中 + 期末考试<br>[复习资料](./Term4/Computer-Networking/Reviews)<br>[往年题](./Term4/Computer-Networking/Past-Exams) |
| [形式语言与自动机](./Term4/Formal-Languages-and-Automata) | 必修 | 2 | [平时作业](./Term4/Formal-Languages-and-Automata/Homeworks)<br>[实验一](https://github.com/Yokumii/BuptLab_FLA_nfa2dfa)<br>[实验二](https://github.com/1BIMU/BuptLab_FLA_CFG-PDA) | 期中 + 期末考试<br>[往年题](./Term4/Formal-Languages-and-Automata/Past-Exams) |
| [数字逻辑与数字系统课程设计](./Term4/Digital-Logic-and-Digital-Systems-Course-Project) | 选修 | 2 | / | [课设仓库](https://github.com/Gh-Shinku/DigitalElecDesign) |
| [计算机网络课程设计](./Term4/Computer-Networking-Course-Project) | 选修 | 1.5 | / | [课设仓库](https://github.com/Gh-Shinku/BUPT-NetworkDesign) |
| 数据结构课程设计 | 选修 | 1.5 | / | [课设前端](https://github.com/Yokumii/BYRTravel)<br>[课设后端](https://github.com/Yokumii/Backend-of-BYRTravel) |
| 毛概 | 必修 | 2.5 + 0.5 | 微电影 | 期末考试<br>[一些复习资料](./Term4/Introduction-to-Maoism) |

### 第五学期

| 课程名称       | 课程性质      | 课程学分 | 作业/实验                                               | 期末考核 |
| -------------- | ------------- | -------- | ------------------------------------------------------- | -------- |
| [算法设计与分析](./Term5/Design-and-Analysis-of-Algorithms) | 必修 | 2    | [个人实验代码及报告](./Term5/Design-and-Analysis-of-Algorithms/Labs) | 期末考试<br>[一些参考资料](./Term5/Design-and-Analysis-of-Algorithms/Reviews) |
| [数据库系统原理](./Term5/DataBase-System-Concepts) | 必修 | 3 | [章节作业参考答案](./Term5/DataBase-System-Concepts/Homeworks)<br>[7次实验报告](./Term5/DataBase-System-Concepts/Labs) | 期中 + 期末考试<br>[往年题](./Term5/DataBase-System-Concepts/Reviews) |
| [操作系统](./Term5/Operating-System) | 必修 | 4 | [平时作业](./Term5/Operating-System/Homeworks)<br>[实验报告](./Term5/Operating-System/Labs) | 期中 + 期末考试<br>[往年题](./Term5/Operating-System/Reviews) |
| [编译原理与技术](./Term5/Compiler-Principle-and-Technology) | 必修 | 4 | [平时作业](./Term5/Compiler-Principle-and-Technology/Homeworks)<br>[实验报告](./Term5/Compiler-Principle-and-Technology/Labs) | 期中 + 期末考试<br>[往年题](./Term5/Compiler-Principle-and-Technology/Reviews) |
| [计算机网络技术实践](./Term5/Computer-Networking-Practical) | 选修 | 2 | [2次实验](./Term5/Computer-Networking-Practical/Labs) | 实验报告 + 线下验收 |
| [Python程序设计](./Term5/Python-Programming) | 选修 | 2 | OJ<br>[三次小作业](./Term5/Python-Programming/Homeworks) | [大作业](./Term5/Python-Programming/Finalwork) |
| [网络存储技术](./Term5/Network-Storage-Technologies) | 选修 | 2 | [6次小论文](./Term5/Network-Storage-Technologies/Homeworks) | [大论文](./Term5/Network-Storage-Technologies/Finalworks) |
| [程序设计实践](./Term5/Literate-Programming) | 选修 | 2 | [4次作业](./Term5/Literate-Programming/Homeworks) | [大作业](./Term5/Literate-Programming/Finalworks) |

### 培养方案

1. [计算机学院培养方案2022版](./Additional-Information/Cultivation/计算机学院22版培养方案0927.pdf)
2. [计算机学院培养方案2023版](./Additional-Information/Cultivation/计算机学院（国家示范性软件学院）2023级本科专业培养方案-0831.pdf)

### 转专业

* [计算机类转专业指导](./Additional-Information/Change-Major/计算机类转专业指导.pdf)

> 参考资料来源于周行算法协会针对2023级转专业的内部指导资料，侵删。

## 妙妙工具

### 期末一键评教

- 脚本地址：[bupt-jwgl-evaluation-autofill.js](./Scripts/bupt-jwgl-evaluation-autofill.js)
- 食用方法：在期末评教页面打开浏览器控制台，粘贴脚本内容并回车，即可自动填充评教表单。注意，脚本默认不会自动提交，如需自动提交可将 `CONFIG.finalSubmit` 改为 `true` 再运行，但**请务必在提交前检查评教内容，确保符合实际情况！**

## Awesome

本人在收集时参考了以下仓库或网站的部分资料：

- [BUPT-SCS-Courses](https://github.com/oneliey/BUPT-SCS-Courses.git)
- [BUPT_SCS_Resources](https://github.com/Cowboy-Spike-Spiegel/BUPT_SCS_Resources)
- [BYRDocs](https://byrdocs.org/)

## 🤝 贡献方式
非常欢迎学弟学妹共同完善本仓库！  
贡献方法：
1. Fork 本仓库。  
2. 在对应的路径添加或更新内容。  
3. 提交 [Pull Request](https://github.com/Yokumii/BUPT-SCS-Courses-Shared/pulls)。  

## 许可证

See the [LICENSE](./LICENSE) for more details.

---

<div align="center">
  <i>Curated and maintained by Yokumi</i>
</div>
