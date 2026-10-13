<template>
  <el-card class="auth-card">
    <template #header>注册</template>
    <el-form :model="form" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="submit">注册</el-button>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { registerApi, loginApi } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const form = reactive({ username: "", email: "", password: "" });

async function submit() {
  loading.value = true;
  try {
    await registerApi(form);
    const loginRes = await loginApi({ username: form.username, password: form.password });
    auth.setAuth(loginRes.access_token, loginRes.user);
    ElMessage.success("注册成功");
    router.push("/");
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || "注册失败");
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
