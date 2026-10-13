<template>
  <el-card class="auth-card">
    <template #header>登录</template>
    <el-form :model="form" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="submit">登录</el-button>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { loginApi } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const form = reactive({ username: "", password: "" });

async function submit() {
  loading.value = true;
  try {
    const data = await loginApi(form);
    auth.setAuth(data.access_token, data.user);
    ElMessage.success("登录成功");
    router.push("/");
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "登录失败");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-card {
  max-width: 520px;
}
</style>
