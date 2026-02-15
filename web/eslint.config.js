import pkg from 'eslint';
import next from 'eslint-config-next';

const { defineConfig } = pkg;

export default defineConfig({
  extends: next,
  rules: {
    // 在这里添加自定义规则
  },
});