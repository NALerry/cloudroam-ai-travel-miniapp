<template>
  <view class="profile-page">
    <!-- 用户信息头部 -->
    <view class="user-header">
      <view class="user-bg">
        <image class="bg-image" src="/static/images/bg/profile-bg.jpg" mode="aspectFill"></image>
        <view class="bg-overlay"></view>
      </view>
      
      <!-- 已登录状态 -->
      <view class="user-info" v-if="isLoggedIn">
        <view class="avatar-section">
          <image 
            class="user-avatar" 
            :src="userInfo.avatar" 
            mode="aspectFill"
            @tap="changeAvatar"
          ></image>
          <view class="avatar-edit" @tap="changeAvatar">
            <image src="/static/icons/general/camera.png" class="edit-icon"></image>
          </view>
        </view>
        
        <view class="user-main">
          <view class="user-basic">
            <text class="user-name">{{ userInfo.nickname }}</text>
            <text class="user-bio">{{ userInfo.bio || '这个人很懒，什么都没有写～' }}</text>
          </view>
          
          <!-- 删除统计区域 -->
        </view>
        
        <view class="edit-profile" @tap="editProfile">
          <text>编辑资料</text>
        </view>
      </view>

      <!-- 未登录状态 -->
      <view class="user-info" v-else>
        <view class="avatar-section">
          <image class="user-avatar" src="/static/avatars/default.png" mode="aspectFill"></image>
        </view>
        <view class="user-main">
          <view class="user-basic">
            <text class="user-name">未登录</text>
            <text class="user-bio">登录后享受完整功能</text>
          </view>
        </view>
        <view class="login-btn" @tap="navigateToLogin">
          <text>立即登录</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <scroll-view class="menu-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 我的内容 -->
      <view class="menu-section">
        <view class="section-header">
          <text class="section-title">我的内容</text>
        </view>
        <view class="menu-grid">
          <view class="menu-item" @tap="navigateToWithAuth('myPosts')">
            <view class="menu-icon post">
              <image src="/static/icons/general/post.png" class="icon-img"></image>
            </view>
            <text class="menu-text">我的投稿</text>
            <!-- 移除消息提示 -->
          </view>
          
          <view class="menu-item" @tap="navigateToWithAuth('myCollections')">
            <view class="menu-icon collection">
              <image src="/static/icons/general/favorite.png" class="icon-img"></image>
            </view>
            <text class="menu-text">我的收藏</text>
            <!-- 删除红标 -->
          </view>
          
          <view class="menu-item" @tap="navigateToWithAuth('myLikes')">
            <view class="menu-icon like">
              <image src="/static/icons/general/like.png" class="icon-img"></image>
            </view>
            <text class="menu-text">我的点赞</text>
            <!-- 移除消息提示 -->
          </view>
          
          <view class="menu-item" @tap="navigateToWithAuth('myHistory')">
            <view class="menu-icon history">
              <image src="/static/icons/general/browsinghistory.png" class="icon-img"></image>
            </view>
            <text class="menu-text">浏览历史</text>
          </view>
        </view>
      </view>

      <!-- 旅行工具 -->
      <view class="menu-section">
        <view class="section-header">
          <text class="section-title">旅行工具</text>
        </view>
        <view class="menu-list">
          <!-- 已删除"我的行程"板块 -->
          
          <view class="menu-row" @tap="navigateToWithAuth('myBookmarks')">
            <view class="row-left">
              <view class="row-icon">
                <image src="/static/icons/general/gps.png" class="row-icon-img"></image>
              </view>
              <text class="row-text">地点收藏</text>
            </view>
            <image src="/static/icons/general/right.png" class="arrow-icon"></image>
          </view>
          
          <view class="menu-row" @tap="navigateToWithAuth('myRoutes')">
            <view class="row-left">
              <view class="row-icon">
                <image src="/static/icons/general/path1.png" class="row-icon-img"></image>
              </view>
              <text class="row-text">我的路线</text>
            </view>
            <image src="/static/icons/general/right.png" class="arrow-icon"></image>
          </view>
          
          <view class="menu-row" @tap="navigateToWithAuth('travelNotes')">
            <view class="row-left">
              <view class="row-icon">
                <image src="/static/icons/general/book.png" class="row-icon-img"></image>
              </view>
              <text class="row-text">旅行笔记</text>
            </view>
            <image src="/static/icons/general/right.png" class="arrow-icon"></image>
          </view>
        </view>
      </view>

      <!-- 账号设置 -->
      <view class="menu-section">
        <view class="section-header">
          <text class="section-title">账号设置</text>
        </view>
        <view class="menu-list">
          <view class="menu-row" @tap="navigateTo('settings')">
            <view class="row-left">
              <view class="row-icon">
                <image src="/static/icons/general/setting.png" class="row-icon-img"></image>
              </view>
              <text class="row-text">系统设置</text>
            </view>
            <image src="/static/icons/general/right.png" class="arrow-icon"></image>
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 版本信息 -->
    <view class="version-info">
      <text>版本号 {{ appVersion }}</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      userInfo: {
        id: null,
        avatar: '/static/avatars/touxiang.png',
        nickname: '旅行者',
        bio: '热爱旅行，探索未知的世界',
        followCount: 128,
        fansCount: 456,
        likeCount: 1234,
        postCount: 23,
        collectionCount: 56
      },
      isLoggedIn: false,
      appVersion: '1.0.0',
      isLoading: false,
      scrollHeight: 0,
      isUploadingAvatar: false,
      BASE_URL: 'http://localhost:8080/api'
    }
  },
  onLoad() {
    this.checkLoginStatus()
    this.initPage()
    this.calculateScrollHeight()
  },
  
  onShow() {
    this.checkLoginStatus()
    this.loadUserInfo()
  },
  
  onPullDownRefresh() {
    this.refreshData()
  },
  
  onResize() {
    this.calculateScrollHeight()
  },
  
  methods: {
    // 计算滚动区域高度
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      
      let availableHeight = windowHeight - statusBarHeight - navigationBarHeight
      this.scrollHeight = availableHeight
    },
    
    // 初始化页面
    async initPage() {
      this.isLoading = true
      await this.loadUserInfo()
      this.isLoading = false
    },
    
    // 检查登录状态
    checkLoginStatus() {
      const token = uni.getStorageSync('user_token')
      const userInfo = uni.getStorageSync('user_info')
      this.isLoggedIn = !!(token && userInfo)
      
      if (this.isLoggedIn && userInfo) {
        this.userInfo = { ...this.userInfo, ...userInfo }
        this.ensureValidAvatar()
      }
    },
    
    // 确保头像有效 - 修复头像URL处理
    ensureValidAvatar() {
      if (!this.userInfo.avatar) {
        this.userInfo.avatar = '/static/avatars/touxiang.png'
        return
      }
      
      console.log('原始头像URL:', this.userInfo.avatar)
      
      // 如果是相对路径且不是默认头像，添加基础URL
      if (this.userInfo.avatar.startsWith('/uploads/')) {
        // 上传的头像URL，确保可以正确访问
        this.userInfo.avatar = 'http://localhost:8080' + this.userInfo.avatar
        console.log('处理后头像URL:', this.userInfo.avatar)
      } else if (this.userInfo.avatar.startsWith('http://tmp/') || 
                 this.userInfo.avatar.includes('tempFilePaths') ||
                 (this.userInfo.avatar.startsWith('data:image') && this.userInfo.avatar.length > 10000)) {
        // 明显无效的头像使用默认头像
        this.userInfo.avatar = '/static/avatars/touxiang.png'
        console.log('使用默认头像')
      } else if (this.userInfo.avatar.startsWith('/static/')) {
        // 静态资源路径保持不变
        console.log('使用静态资源头像')
      }
      // 其他情况（包括完整URL）保持不变
    },
    
    // 刷新数据
    async refreshData() {
      await this.loadUserInfo()
      uni.stopPullDownRefresh()
    },
    
    // 加载用户信息 - 修复头像处理
    async loadUserInfo() {
      try {
        const localUserInfo = uni.getStorageSync('user_info')
        const token = uni.getStorageSync('user_token')
        
        if (!localUserInfo || !localUserInfo.id || !token) {
          console.log('未找到用户信息或token')
          return
        }
        
        console.log('开始加载用户信息，用户ID:', localUserInfo.id)
        
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `${this.BASE_URL}/users/${localUserInfo.id}`,
            method: 'GET',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            success: (res) => {
              console.log('API响应:', res)
              resolve(res)
            },
            fail: (err) => {
              console.error('API请求失败:', err)
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          const apiUserInfo = res.data.data
          console.log('API返回的用户信息:', apiUserInfo)
          
          // 修复头像处理逻辑
          let avatar = apiUserInfo.avatar
          if (!avatar) {
            avatar = '/static/avatars/touxiang.png'
          } else if (avatar.startsWith('/uploads/')) {
            // 上传的头像URL，添加基础URL
            avatar = 'http://localhost:8080' + avatar
          } else if (avatar.startsWith('http://tmp/') || 
                     avatar.includes('tempFilePaths') ||
                     (avatar.startsWith('data:image') && avatar.length > 10000)) {
            // 明显无效的头像使用默认头像
            avatar = '/static/avatars/touxiang.png'
          }
          // 上传的头像URL（/uploads/avatars/...）和静态资源保持不变
          
          this.userInfo = { 
            ...this.userInfo, 
            ...apiUserInfo,
            avatar: avatar,
            // 不再需要这些统计字段
            followCount: 0,
            fansCount: 0,
            likeCount: 0,
            postCount: apiUserInfo.postCount || 0,
            collectionCount: apiUserInfo.collectionCount || 0
          }
          
          uni.setStorageSync('user_info', this.userInfo)
          console.log('用户信息加载成功，头像:', this.userInfo.avatar)
        } else {
          console.warn('API返回异常:', res)
          if (res.statusCode === 400) {
            this.showError('用户不存在，请重新登录')
            uni.removeStorageSync('user_token')
            uni.removeStorageSync('user_info')
            this.isLoggedIn = false
            return
          }
          throw new Error(res.data?.message || '获取用户信息失败')
        }
      } catch (error) {
        console.error('加载用户信息失败:', error)
        const localUserInfo = uni.getStorageSync('user_info')
        if (localUserInfo) {
          this.userInfo = { ...this.userInfo, ...localUserInfo }
          this.ensureValidAvatar()
          this.showError('加载失败，使用缓存数据')
        }
      }
    },
    
    // 更换头像
    changeAvatar() {
      if (!this.isLoggedIn) {
        this.navigateToLogin()
        return
      }
      
      if (this.isLoading || this.isUploadingAvatar) return
      
      uni.showActionSheet({
        itemList: ['拍照', '从相册选择'],
        success: (res) => {
          const sourceType = res.tapIndex === 0 ? ['camera'] : ['album']
          this.chooseImage(sourceType)
        },
        fail: () => {
          this.showError('操作取消')
        }
      })
    },
    
    // 选择图片
    chooseImage(sourceType) {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: sourceType,
        success: (chooseRes) => {
          this.uploadAvatar(chooseRes.tempFilePaths[0])
        },
        fail: (error) => {
          console.error('选择图片失败:', error)
          this.showError('选择图片失败')
        }
      })
    },
    
    // 上传头像到服务器
    async uploadAvatar(tempFilePath) {
      if (this.isUploadingAvatar) return
      
      this.isUploadingAvatar = true
      uni.showLoading({
        title: '上传中...',
        mask: true
      })
      
      try {
        const token = uni.getStorageSync('user_token')
        const userId = this.userInfo.id
        
        if (!userId || !token) {
          throw new Error('用户未登录')
        }
        
        console.log('开始上传头像，用户ID:', userId)
        
        // 使用 uni.uploadFile 上传文件
        const uploadRes = await new Promise((resolve, reject) => {
          uni.uploadFile({
            url: `${this.BASE_URL}/upload/avatar`,
            filePath: tempFilePath,
            name: 'file',
            formData: {
              userId: userId
            },
            header: {
              'Authorization': `Bearer ${token}`
            },
            success: (res) => {
              console.log('上传文件响应:', res)
              try {
                const data = JSON.parse(res.data)
                resolve({ statusCode: res.statusCode, data: data })
              } catch (e) {
                reject(new Error('解析响应失败: ' + e.message))
              }
            },
            fail: (err) => {
              console.error('上传文件失败:', err)
              reject(err)
            }
          })
        })
        
        if (uploadRes.statusCode === 200 && uploadRes.data && uploadRes.data.success) {
          const avatarUrl = uploadRes.data.url
          console.log('头像上传成功，URL:', avatarUrl)
          
          // 更新头像URL到用户信息
          await this.updateAvatarToServer(avatarUrl)
          
        } else {
          throw new Error(uploadRes.data?.message || '头像上传失败')
        }
      } catch (error) {
        console.error('上传头像失败:', error)
        this.showError('上传失败: ' + error.message)
      } finally {
        this.isUploadingAvatar = false
        uni.hideLoading()
      }
    },
    
    // 更新头像URL到服务器
    async updateAvatarToServer(avatarUrl) {
      try {
        const token = uni.getStorageSync('user_token')
        const userId = this.userInfo.id
        
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `${this.BASE_URL}/users/${userId}/avatar`,
            method: 'PUT',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            data: {
              avatar: avatarUrl
            },
            success: (res) => {
              console.log('更新头像响应:', res)
              resolve(res)
            },
            fail: (err) => {
              console.error('更新头像请求失败:', err)
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          // 更新本地数据 - 确保头像URL正确
          const processedAvatarUrl = 'http://localhost:8080' + avatarUrl
          this.userInfo.avatar = processedAvatarUrl
          
          // 更新本地存储
          const updatedUserInfo = { ...this.userInfo, avatar: processedAvatarUrl }
          uni.setStorageSync('user_info', updatedUserInfo)
          
          this.showSuccess('头像更新成功')
          
          // 重新加载用户信息确保数据一致
          setTimeout(() => {
            this.loadUserInfo()
          }, 500)
        } else {
          throw new Error(res.data?.message || '更新头像失败')
        }
      } catch (error) {
        console.error('更新头像到服务器失败:', error)
        this.showError('头像保存失败: ' + error.message)
      }
    },
    
    // 编辑资料
    editProfile() {
      if (!this.isLoggedIn) {
        this.navigateToLogin()
        return
      }
      uni.navigateTo({
        url: '/pages/profile-edit/profile-edit'
      })
    },
    
    // 跳转到登录页
    navigateToLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
    },
    
    // 删除导航到统计页面的方法
    // navigateToStat() 方法已删除
    
    // 导航到不同页面（需要登录）
    navigateToWithAuth(page) {
      if (!this.isLoggedIn) {
        this.navigateToLogin()
        return
      }
      this.navigateTo(page)
    },
    
    // 导航到不同页面
    navigateTo(page) {
      const routeMap = {
        'myPosts': '/pages/my-posts/my-posts',
        'myCollections': '/pages/my-collections/my-collections',
        'myLikes': '/pages/my-likes/my-likes',
        'myHistory': '/pages/my-history/my-history',
        'myBookmarks': '/pages/my-bookmarks/my-bookmarks',
        'myRoutes': '/pages/my-routes/my-routes',
        'travelNotes': '/pages/travel-notes/travel-notes',
        'settings': '/pages/settings/settings'
      }
      
      if (routeMap[page]) {
        uni.navigateTo({
          url: routeMap[page]
        })
      } else {
        this.showToast('功能开发中')
      }
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
    },
    
    // 显示普通提示
    showToast(message) {
      uni.showToast({
        title: message,
        icon: 'none',
        duration: 2000
      })
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
}

/* 用户头部样式 */
.user-header {
  position: relative;
  height: 280rpx; /* 调整高度以适应删除统计区域 */
}

.user-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.bg-image {
  width: 100%;
  height: 100%;
}

.bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.2));
}

.user-info {
  position: relative;
  z-index: 2;
  padding: 40rpx 30rpx 30rpx;
  display: flex;
  align-items: flex-start;
  gap: 24rpx;
}

.avatar-section {
  position: relative;
  flex-shrink: 0;
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.9);
  background-color: #fff;
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36rpx;
  height: 36rpx;
  background: #b8d4ff;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #fff;
}

.edit-icon {
  width: 18rpx;
  height: 18rpx;
}

.user-main {
  flex: 1;
  min-width: 0;
}

.user-basic {
  margin-bottom: 0; /* 删除统计区域后不需要下边距 */
}

.user-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 8rpx;
}

.user-bio {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  display: block;
  line-height: 1.4;
}

/* 删除统计区域样式 */
/* .user-stats 相关样式已删除 */

.edit-profile {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  color: #fff;
  font-size: 24rpx;
  flex-shrink: 0;
  height: fit-content;
}

/* 未登录状态的登录按钮 */
.login-btn {
  background: rgba(255, 255, 255, 0.9);
  padding: 16rpx 32rpx;
  border-radius: 24rpx;
  color: #b8d4ff;
  font-size: 26rpx;
  font-weight: 500;
  flex-shrink: 0;
  height: fit-content;
}

/* 菜单滚动区域 */
.menu-scroll {
  flex: 1;
  background: #f8f8f8;
  margin-top: -30rpx;
  border-top-left-radius: 30rpx;
  border-top-right-radius: 30rpx;
  position: relative;
  z-index: 3;
}

.menu-section {
  background: #fff;
  margin: 20rpx 0;
  border-radius: 0;
}

.section-header {
  padding: 30rpx 30rpx 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

/* 网格菜单样式 */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding: 20rpx 0;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20rpx 0;
  position: relative;
}

.menu-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.menu-icon.post {
  background: #e8f1ff;
}

.menu-icon.collection {
  background: #fff0e8;
}

.menu-icon.like {
  background: #ffe8e8;
}

.menu-icon.history {
  background: #f0e8ff;
}

.icon-img {
  width: 36rpx;
  height: 36rpx;
}

.menu-text {
  font-size: 24rpx;
  color: #666;
}

/* 删除红标样式 */
/* .menu-badge 相关样式已删除 */

/* 列表菜单样式 */
.menu-list {
  background: #fff;
}

.menu-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 30rpx;
  border-bottom: 1rpx solid #f8f8f8;
}

.menu-row:last-child {
  border-bottom: none;
}

.row-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.row-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.row-icon-img {
  width: 28rpx;
  height: 28rpx;
}

.row-text {
  font-size: 28rpx;
  color: #333;
}

.arrow-icon {
  width: 24rpx;
  height: 24rpx;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}

/* 版本信息 */
.version-info {
  text-align: center;
  padding: 30rpx;
  background: #f8f8f8;
}

.version-info text {
  font-size: 24rpx;
  color: #999;
}
</style>