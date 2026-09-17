import App from './App'

// 配置请求基地址（根据您的后端地址修改）
const BASE_URL = 'http://localhost:8080'; // 修改为您的后端地址

// 封装 uni.request
const http = {
  get(url, data = {}) {
    return new Promise((resolve, reject) => {
      uni.request({
        url: BASE_URL + url,
        method: 'GET',
        data: data,
        success: (res) => resolve(res),
        fail: (err) => reject(err)
      });
    });
  },
  
  post(url, data = {}) {
    return new Promise((resolve, reject) => {
      uni.request({
        url: BASE_URL + url,
        method: 'POST',
        data: data,
        header: {
          'Content-Type': 'application/json'
        },
        success: (res) => resolve(res),
        fail: (err) => reject(err)
      });
    });
  },
  
  put(url, data = {}) {
    return new Promise((resolve, reject) => {
      uni.request({
        url: BASE_URL + url,
        method: 'PUT',
        data: data,
        header: {
          'Content-Type': 'application/json'
        },
        success: (res) => resolve(res),
        fail: (err) => reject(err)
      });
    });
  },
  
  delete(url) {
    return new Promise((resolve, reject) => {
      uni.request({
        url: BASE_URL + url,
        method: 'DELETE',
        success: (res) => resolve(res),
        fail: (err) => reject(err)
      });
    });
  }
};

// #ifndef VUE3
import Vue from 'vue'
import './uni.promisify.adaptor'
Vue.config.productionTip = false

// 将 http 挂载到 Vue 原型上
Vue.prototype.$http = http;

App.mpType = 'app'
const app = new Vue({
  ...App
})
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'

export function createApp() {
  const app = createSSRApp(App)
  
  // 在 Vue3 中提供全局属性
  app.config.globalProperties.$http = http;
  
  return {
    app
  }
}
// #endif