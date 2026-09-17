// utils/auth.js
export default {
  // 微信登录
  wechatLogin() {
    return new Promise((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: (loginRes) => {
          // 发送code到后端
          uni.request({
            url: 'https://your-api.com/auth/login',
            method: 'POST',
            data: { code: loginRes.code },
            success: (res) => {
              // 存储token
              uni.setStorageSync('token', res.data.token)
              uni.setStorageSync('userInfo', res.data.userInfo)
              resolve(res.data)
            },
            fail: reject
          })
        },
        fail: reject
      })
    })
  },
  
  // 检查登录状态
  checkLogin() {
    const token = uni.getStorageSync('token')
    return !!token
  }
}