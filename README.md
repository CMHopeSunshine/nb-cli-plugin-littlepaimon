<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img src="https://cli.nonebot.dev/logo.png" width="200" height="200" alt="nonebot">
</p>

<div align="center">

# NB CLI Plugin For LittlePaimon

_✨ 为小派蒙Bot定制的 NoneBot2 CLI 插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/CMHopeSunshine/nb-cli-plugin-littlepaimon.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nb-cli-plugin-littlepaimon">
    <img src="https://img.shields.io/pypi/v/nb-cli-plugin-littlepaimon.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">


</div>

## 安装

<details>
<summary>安装nb-cli</summary>

> 请确保你的Python版本为3.8+，且在环境变量中

<details>
<summary>通过 pipx 安装</summary>

```shell
pip install --user pipx
pipx ensurepath
pipx install nb-cli
```
</details>

<details>
<summary>通过 pip 安装</summary>

```shell
pip install nb-cli
```
</details>

</details>

<details>
<summary>安装本插件</summary>

<details>
<summary>通过 nb-cli 安装</summary>

```shell
nb self install nb-cli-plugin-littlepaimon
```

</details>

<details>
<summary>通过 pipx 安装</summary>

```shell
pipx inject nb-cli nb-cli-plugin-littlepaimon
```
</details>

<details>
<summary>通过 pip 安装</summary>

```shell
pip install nb-cli-plugin-littlepaimon
```
</details>

</details>

<details>
<summary>安装Git</summary>

~~能上Github的话，应该都会装Git吧)~~

</details>

## 使用

- `nb paimon` 交互式使用
  - `nb paimon create` 
    - 交互式指引安装[小派蒙Bot](https://github.com/CMHopeSunshine/LittlePaimon)
    - 自动克隆源码、创建虚拟环境、安装依赖，下载并配置go-cqhttp
  - `nb paimon install` 安装依赖库到小派蒙环境中
  - `nb paimon res` 下载或更新小派蒙的资源
  - `nb paimon logo` 展示小派蒙的logo

## TODO

- [x] 更新资源
- [ ] 自动安装git
- [ ] 修改配置
- [ ] 安装小派蒙插件
- [ ] more