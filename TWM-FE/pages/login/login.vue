<template>
  <view class="login-page">
    <!-- 蓝白渐变背景层 -->
    <view class="login-bg-gradient"></view>
    
    <!-- 内容区域 -->
    <view class="login-content">
      <!-- 头部标题 -->
      <view class="login-header">
        <text class="welcome-text">欢迎使用云游志</text>
        <text class="sub-title">记录每一次精彩的旅行</text>
      </view>

      <!-- 登录方式选择 -->
      <view class="login-methods">
        <!-- 微信一键登录 -->
        <view class="method-section">
          <button 
            class="login-btn wechat-login" 
            :disabled="isLoading"
            @tap="handleWechatLogin"
            open-type="getUserInfo"
            @getuserinfo="onGetUserInfo"
          >
            <view class="btn-content">
              <image src="/static/icons/general/wechat.png" class="btn-icon"></image>
              <text class="btn-text">微信一键登录</text>
            </view>
          </button>
          <text class="method-tip">推荐使用，快速安全</text>
        </view>

        <!-- 分割线 -->
        <view class="divider">
          <view class="divider-line"></view>
          <text class="divider-text">或</text>
          <view class="divider-line"></view>
        </view>

        <!-- 手机号登录 -->
        <view class="method-section">
          <button 
            class="login-btn phone-login" 
            :disabled="isLoading"
            @tap="handlePhoneLogin"
          >
            <view class="btn-content">
              <image src="/static/icons/general/phone.png" class="btn-icon"></image>
              <text class="btn-text">手机号登录</text>
            </view>
          </button>
          <text class="method-tip">使用手机号登录</text>
        </view>
      </view>

      <!-- 协议提示 -->
      <view class="agreement-tip">
        <text class="tip-text">登录即代表您同意</text>
        <text class="agreement-link" @tap="navigateToAgreement">《用户协议》</text>
        <text class="tip-text">和</text>
        <text class="agreement-link" @tap="navigateToPrivacy">《隐私政策》</text>
      </view>
    </view>

    <!-- 手机号登录弹窗 -->
    <view class="phone-login-modal" v-if="showPhoneModal">
      <view class="modal-mask" @tap="closePhoneModal"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">手机号登录</text>
          <view class="modal-close" @tap="closePhoneModal">
            <image src="/static/icons/general/close.png" class="close-icon"></image>
          </view>
        </view>
        
        <view class="modal-body">
          <view class="phone-input-group">
            <view class="input-item">
              <view class="input-left">
                <text class="area-code">+86</text>
              </view>
              <input
                class="phone-input"
                type="number"
                placeholder="请输入手机号码"
                placeholder-class="input-placeholder"
                v-model="phoneForm.phoneNumber"
                maxlength="11"
              />
            </view>

            <view class="input-item">
              <view class="input-left">
                <image src="/static/icons/general/lock.png" class="input-icon"></image>
              </view>
              <input
                class="code-input"
                type="number"
                placeholder="请输入验证码"
                placeholder-class="input-placeholder"
                v-model="phoneForm.verificationCode"
                maxlength="6"
              />
              <view class="get-code-btn" @tap="getVerificationCode" :class="{ disabled: countdown > 0 }">
                <text class="code-text">{{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}</text>
              </view>
            </view>
          </view>

          <button 
            class="confirm-btn" 
            :class="{ disabled: !canConfirm }" 
            :disabled="!canConfirm || isLoading"
            @tap="confirmPhoneLogin"
          >
            <text class="confirm-text">{{ isLoading ? '登录中...' : '登录' }}</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isLoading: false,
      showPhoneModal: false,
      countdown: 0,
      phoneForm: {
        phoneNumber: '',
        verificationCode: ''
      }
    }
  },
  computed: {
    canConfirm() {
      return this.phoneForm.phoneNumber.trim().length === 11 && 
             this.phoneForm.verificationCode.trim().length === 6
    }
  },
  onLoad() {
    // 检查是否有登录状态，如果有则直接跳转
    this.checkLoginStatus()
  },
  methods: {
    // 检查登录状态
    checkLoginStatus() {
      const token = uni.getStorageSync('user_token')
      if (token) {
        // 已有登录状态，直接跳转到个人中心
        uni.switchTab({
          url: '/pages/profile/profile'
        })
      }
    },
    
    // 微信登录
    handleWechatLogin() {
      if (this.isLoading) return
      
      // 微信登录会自动触发 getUserInfo 事件
      // 这里只是设置加载状态
      this.isLoading = true
    },
    
    // 获取用户信息回调
    async onGetUserInfo(e) {
      if (e.detail.errMsg === 'getUserInfo:ok') {
        // 用户同意授权
        await this.processWechatLogin(e.detail)
      } else {
        // 用户拒绝授权
        this.isLoading = false
        this.showError('您已取消微信授权')
      }
    },
    
    // 处理微信登录
    async processWechatLogin(userInfo) {
      try {
        // 1. 调用 wx.login 获取 code
        const loginRes = await new Promise((resolve, reject) => {
          uni.login({
            provider: 'weixin',
            success: resolve,
            fail: reject
          })
        })
        
        if (loginRes.code) {
          // 2. 模拟向服务器发送 code 和用户信息
          const loginData = await this.mockWechatLogin(loginRes.code, userInfo)
          
          // 3. 保存登录状态
          this.saveLoginState(loginData)
          
          // 4. 显示成功提示并跳转
          this.showSuccess('登录成功')
          
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/profile/profile'
            })
          }, 1500)
        } else {
          throw new Error('微信登录失败')
        }
      } catch (error) {
        console.error('微信登录失败:', error)
        this.showError('登录失败，请重试')
      } finally {
        this.isLoading = false
      }
    },
    
    // 模拟微信登录
mockWechatLogin(code, userInfo) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        token: 'wechat_token_' + Date.now(),
        userInfo: {
          id: 1, // 使用数据库中存在的用户ID
          nickname: userInfo.userInfo.nickName || '微信用户',
          avatar: userInfo.userInfo.avatarUrl || '/static/avatars/touxiang.png',
          bio: '这个人很懒，什么都没有写～',
          followCount: 0,
          fansCount: 0,
          likeCount: 0,
          postCount: 0,
          collectionCount: 0
        }
      })
    }, 1500)
  })
},
    
    // 手机号登录
    handlePhoneLogin() {
      this.showPhoneModal = true
    },
    
    // 关闭手机号登录弹窗
    closePhoneModal() {
      this.showPhoneModal = false
      this.phoneForm = {
        phoneNumber: '',
        verificationCode: ''
      }
    },
    
    // 获取验证码
    async getVerificationCode() {
      if (this.countdown > 0) return
      
      if (!this.phoneForm.phoneNumber || this.phoneForm.phoneNumber.length !== 11) {
        this.showError('请输入正确的手机号码')
        return
      }
      
      // 模拟发送验证码
      this.isLoading = true
      try {
        await this.mockSendVerificationCode()
        this.startCountdown()
        this.showSuccess('验证码已发送')
      } catch (error) {
        this.showError('发送验证码失败')
      } finally {
        this.isLoading = false
      }
    },
    
    // 模拟发送验证码
    mockSendVerificationCode() {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve()
        }, 1000)
      })
    },
    
    // 开始倒计时
    startCountdown() {
      this.countdown = 60
      const timer = setInterval(() => {
        if (this.countdown <= 0) {
          clearInterval(timer)
          return
        }
        this.countdown--
      }, 1000)
    },
    
    // 确认手机号登录
    async confirmPhoneLogin() {
      if (this.isLoading) return
      
      if (!this.validatePhoneForm()) {
        return
      }
      
      this.isLoading = true
      
      try {
        // 模拟手机号登录
        const loginData = await this.mockPhoneLogin()
        
        // 保存登录状态
        this.saveLoginState(loginData)
        
        // 关闭弹窗
        this.closePhoneModal()
        
        // 显示成功提示
        this.showSuccess('登录成功')
        
        // 跳转到个人中心
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/profile/profile'
          })
        }, 1500)
        
      } catch (error) {
        console.error('手机号登录失败:', error)
        this.showError('登录失败，请重试')
      } finally {
        this.isLoading = false
      }
    },
    
    // 验证手机号表单
    validatePhoneForm() {
      if (!this.phoneForm.phoneNumber) {
        this.showError('请输入手机号码')
        return false
      }
      
      if (!/^1[3-9]\d{9}$/.test(this.phoneForm.phoneNumber)) {
        this.showError('请输入正确的手机号码')
        return false
      }
      
      if (!this.phoneForm.verificationCode) {
        this.showError('请输入验证码')
        return false
      }
      
      if (this.phoneForm.verificationCode.length !== 6) {
        this.showError('请输入6位验证码')
        return false
      }
      
      return true
    },
    
mockPhoneLogin() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        token: 'phone_token_' + Date.now(),
        userInfo: {
          id: 1, // 使用数据库中存在的用户ID
          nickname: '手机用户',
          avatar: '/static/avatars/touxiang.png',
          bio: '这个人很懒，什么都没有写～',
          followCount: 0,
          fansCount: 0,
          likeCount: 0,
          postCount: 0,
          collectionCount: 0
        }
      })
    }, 1500)
  })
},
    
    // 保存登录状态
    saveLoginState(loginData) {
      // 保存用户信息
      uni.setStorageSync('user_info', loginData.userInfo)
      uni.setStorageSync('user_token', loginData.token)
    },
    
    // 跳转到用户协议
    navigateToAgreement() {
      uni.navigateTo({
        url: '/pages/agreement/agreement'
      })
    },
    
    // 跳转到隐私政策
    navigateToPrivacy() {
      uni.navigateTo({
        url: '/pages/privacy/privacy'
      })
    },
    
    // 显示成功提示
    showSuccess(message) {
      uni.showToast({
        title: message,
        icon: 'success',
        duration: 2000
      })
    },
    
    // 显示错误提示
    showError(message) {
      uni.showToast({
        title: message,
        icon: 'none',
        duration: 3000
      })
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  /* 备用背景色 */
  background: #f8f8f8;
}

/* 蓝白渐变背景 */
.login-bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  background: linear-gradient(135deg, #b8d4ff 0%, #e8f0fe 100%);
}

/* 内容区域 */
.login-content {
  position: relative;
  z-index: 2;
  padding: 120rpx 60rpx 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120rpx);
}

.login-header {
  text-align: center;
  margin-bottom: 120rpx;
}

.welcome-text {
  font-size: 48rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 16rpx;
  text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.2);
}

.sub-title {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.15);
}

/* 登录方式 */
.login-methods {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.method-section {
  margin-bottom: 60rpx;
  text-align: center;
}

.login-btn {
  width: 100%;
  height: 96rpx;
  border-radius: 48rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
  background: transparent;
  position: relative;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}

.login-btn::after {
  border: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 20rpx;
}

.btn-text {
  font-size: 32rpx;
  font-weight: 500;
}

/* 微信登录按钮 */
.wechat-login {
  background: #07C160;
}

.wechat-login .btn-text {
  color: #fff;
}

/* 手机号登录按钮 */
.phone-login {
  background: rgba(255, 255, 255, 0.96);
  border: 2rpx solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10rpx);
}

.phone-login .btn-text {
  color: #333;
}

.method-tip {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.15);
}

/* 分割线 */
.divider {
  display: flex;
  align-items: center;
  margin: 40rpx 0;
}

.divider-line {
  flex: 1;
  height: 1rpx;
  background: rgba(255, 255, 255, 0.5);
}

.divider-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.85);
  padding: 0 20rpx;
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.15);
}

/* 协议提示 */
.agreement-tip {
  text-align: center;
  padding: 40rpx 0;
}

.tip-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.15);
}

.agreement-link {
  font-size: 24rpx;
  color: #b8d4ff;
  font-weight: 500;
  text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.15);
}

/* 手机号登录弹窗 */
.phone-login-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5rpx);
}

.modal-content {
  background: #fff;
  border-radius: 24rpx;
  width: 600rpx;
  max-width: 90vw;
  position: relative;
  z-index: 1000;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40rpx 30rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.modal-close {
  padding: 10rpx;
}

.close-icon {
  width: 32rpx;
  height: 32rpx;
}

.modal-body {
  padding: 40rpx 30rpx;
}

.phone-input-group {
  margin-bottom: 40rpx;
}

.input-item {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 16rpx;
  padding: 0 30rpx;
  margin-bottom: 30rpx;
  height: 100rpx;
  border: 1rpx solid #eee;
}

.input-item:last-child {
  margin-bottom: 0;
}

.input-left {
  margin-right: 20rpx;
}

.area-code {
  font-size: 28rpx;
  color: #333;
}

.input-icon {
  width: 32rpx;
  height: 32rpx;
}

.phone-input, .code-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  height: 100rpx;
}

.input-placeholder {
  font-size: 28rpx;
  color: #999;
}

.get-code-btn {
  background: #b8d4ff;
  padding: 16rpx 24rpx;
  border-radius: 8rpx;
  margin-left: 20rpx;
  transition: all 0.3s;
}

.get-code-btn.disabled {
  background: #f0f0f0;
}

.code-text {
  font-size: 24rpx;
  color: #fff;
  font-weight: 500;
}

.get-code-btn.disabled .code-text {
  color: #999;
}

.confirm-btn {
  width: 100%;
  height: 96rpx;
  background: #b8d4ff;
  border-radius: 48rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: 0 4rpx 16rpx rgba(184, 212, 255, 0.5);
}

.confirm-btn.disabled {
  background: #f0f0f0;
  box-shadow: none;
}

.confirm-text {
  font-size: 32rpx;
  font-weight: 500;
  color: #fff;
}

.confirm-btn.disabled .confirm-text {
  color: #ccc;
}

/* 响应式调整 */
@media (max-height: 600px) {
  .login-content {
    padding: 80rpx 60rpx 0;
  }
  
  .login-header {
    margin-bottom: 80rpx;
  }
}
</style>