# ASR模型测试自动化流程

这个自动化流程用于在icefall环境下测试ASR模型。它会自动下载模型,建立必要的软链接,检查数据链接,并在不同的数据集上执行测试。

## 先决条件

在运行自动化流程之前,请确保满足以下条件:

1. 已经按照之前的README设置好了icefall的docker环境。
2. 需要测试的模型已经准备好,并且可以通过rsync访问。
3. 测试数据集已经准备好,并且在docker容器中的`/tests/prepared_data_devtest`目录下有相应的软链接。

## 使用方法

1. 将所有的脚本文件放在同一个目录下,例如`/path/to/scripts`。

2. 运行`decode.sh`脚本,提供模型目录路径、epoch和docker容器名称作为参数:

   ```bash
   /path/to/scripts/decode.sh /path/to/model/directory epoch docker_name
   ```

   - `/path/to/model/directory`: 模型所在的目录路径,脚本会自动从这个路径中提取模型名称。
   - `epoch`: 模型的epoch数。
   - `docker_name`: 运行icefall环境的docker容器名称。

3. 脚本会自动执行以下步骤:
   - 下载模型到docker容器的`/tests/models`目录下(如果模型还没有下载)。
   - 为commonvoice、gigaspeech、libriheavy和librispeech数据集建立模型软链接。
   - 检查每个数据集的数据软链接是否正确,如果检查失败,脚本会抛出异常并终止。
   - 在每个数据集上执行测试。

4. 测试结果会输出到docker容器的相应目录下。

## 脚本说明

- `decode.sh`: 主脚本,用于执行整个自动化流程。
- `download_model.sh`: 用于下载模型。
- `ln_model.sh`: 用于建立模型软链接。
- `check_data_link.sh`: 用于检查数据软链接是否正确。
- `start_test.sh`: 用于在指定数据集上启动测试。

请确保所有脚本都有可执行权限。如果没有,可以使用以下命令添加可执行权限:

```bash
chmod +x /path/to/scripts/*.sh
```

## 注意事项

- 脚本假设测试数据集位于docker容器的`/tests/prepared_data_devtest`目录下。如果数据集位置有变化,请相应地修改`check_data_link.sh`脚本。
- 如果要添加或移除测试数据集,请相应地修改`decode.sh`、`check_data_link.sh`和`start_test.sh`脚本。