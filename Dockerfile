# 使用Python 3.9镜像，它使用OpenSSL 1.1.x
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgdiplus \
    libicu-dev \
    icu-devtools \
    wget \
    gnupg \
    ca-certificates \
    libssl1.1 \
    libssl-dev \
    openssl \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 .NET 运行时 (Aspose.Words 需要)
RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-runtime-6.0 \
    && rm -rf /var/lib/apt/lists/*

# 在安装命令后添加验证步骤（调试用）
RUN echo "----验证SSL库----" && \
    ls -l /usr/lib/x86_64-linux-gnu/libssl* && \
    openssl version

# 设置环境变量，使 Aspose.Words 使用不变性全球化模式
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true
ENV LDFLAGS="-L/usr/lib/x86_64-linux-gnu"
ENV CFLAGS="-I/usr/include/openssl"
# 添加LD_LIBRARY_PATH环境变量，确保能找到libssl库
ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"

# 先复制依赖文件
COPY requirements.txt .

# 安装Python依赖，修改安装顺序和方式
RUN ldconfig && \
    pip install --no-cache-dir --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple/ wheel setuptools && \
    pip install --no-cache-dir --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple/ cryptography pyOpenSSL && \
    pip install --no-cache-dir --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 7001

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7001", "--proxy-headers"]