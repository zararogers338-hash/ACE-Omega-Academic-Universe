# Security Policy / 安全说明

## Supported version

This open-source preview is provided as-is.

## Reporting issues

Please report security-sensitive issues privately when possible.

## Important risks

- API keys may be stored locally in `config.yaml`; do not commit this file.
- Uploaded files may contain private literature data.
- External AI APIs may receive user prompts and dataset summaries.
- Streamlit does not provide production authentication by default.
- Local model files can be large and should not be committed.

中文：不要提交 `config.yaml`、`.env`、私有文献数据或模型文件。外部 API 可能接收你的数据摘要。不要把没有访问控制的 Streamlit 应用暴露到公网。
