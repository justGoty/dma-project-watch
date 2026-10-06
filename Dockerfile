FROM python:3.13-slim AS build
WORKDIR /build
COPY pyproject.toml README.md LICENSE watch.py dashboard.py ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels .

FROM python:3.13-slim
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir --no-deps /wheels/*.whl
WORKDIR /app
USER 10001:10001
ENTRYPOINT ["dma-watch"]
