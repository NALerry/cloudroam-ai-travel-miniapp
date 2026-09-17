<template>
  <view class="profile-edit-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <image src="/static/icons/general/back.png" class="back-icon"></image>
      </view>
      <view class="nav-title">
        <text>编辑资料</text>
      </view>
      <view class="nav-right" @tap="saveProfile">
        <text class="save-text" :class="{ disabled: !hasChanges }">保存</text>
      </view>
    </view>

    <!-- 编辑内容 -->
    <scroll-view class="edit-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 头像编辑 -->
      <view class="edit-section">
        <view class="section-label">头像</view>
        <view class="avatar-edit-section" @tap="changeAvatar">
          <image class="edit-avatar" :src="editForm.avatar" mode="aspectFill"></image>
          <view class="avatar-edit-mask">
            <image src="/static/icons/general/camera.png" class="camera-icon"></image>
            <text class="edit-text">更换头像</text>
          </view>
        </view>
      </view>

      <!-- 基本信息 -->
      <view class="edit-section">
        <view class="section-label">基本信息</view>
        
        <view class="form-item">
          <view class="item-label">昵称</view>
          <view class="item-content">
            <input
              class="item-input"
              type="text"
              placeholder="请输入昵称"
              placeholder-class="input-placeholder"
              v-model="editForm.nickname"
              maxlength="20"
              @input="onFormChange"
            />
            <text class="word-count">{{ editForm.nickname.length }}/20</text>
          </view>
        </view>

        <view class="form-item">
          <view class="item-label">个性签名</view>
          <view class="item-content">
            <textarea
              class="item-textarea"
              placeholder="介绍一下自己吧～"
              placeholder-class="input-placeholder"
              v-model="editForm.bio"
              maxlength="50"
              @input="onFormChange"
            ></textarea>
            <text class="word-count">{{ editForm.bio.length }}/50</text>
          </view>
        </view>

        <view class="form-item">
          <view class="item-label">性别</view>
          <view class="item-content">
            <picker 
              class="gender-picker"
              mode="selector" 
              :range="genderOptions" 
              :value="genderIndex"
              @change="onGenderChange"
            >
              <view class="picker-content">
                <text class="picker-text" :class="{ placeholder: !editForm.gender }">
                  {{ editForm.gender || '请选择性别' }}
                </text>
                <image src="/static/icons/general/right.png" class="arrow-icon"></image>
              </view>
            </picker>
          </view>
        </view>

        <view class="form-item">
          <view class="item-label">生日</view>
          <view class="item-content">
            <picker 
              class="birthday-picker"
              mode="date" 
              :value="editForm.birthday"
              @change="onBirthdayChange"
            >
              <view class="picker-content">
                <text class="picker-text" :class="{ placeholder: !editForm.birthday }">
                  {{ editForm.birthday || '请选择生日' }}
                </text>
                <image src="/static/icons/general/right.png" class="arrow-icon"></image>
              </view>
            </picker>
          </view>
        </view>
      </view>

      <!-- 联系信息 -->
      <view class="edit-section">
        <view class="section-label">联系信息</view>
        
        <view class="form-item">
          <view class="item-label">手机号</view>
          <view class="item-content">
            <input
              class="item-input"
              type="number"
              placeholder="请输入手机号"
              placeholder-class="input-placeholder"
              v-model="editForm.phone"
              maxlength="11"
              @input="onFormChange"
            />
          </view>
        </view>

        <view class="form-item">
          <view class="item-label">邮箱</view>
          <view class="item-content">
            <input
              class="item-input"
              type="text"
              placeholder="请输入邮箱"
              placeholder-class="input-placeholder"
              v-model="editForm.email"
              @input="onFormChange"
            />
          </view>
        </view>

        <view class="form-item">
          <view class="item-label">所在地</view>
          <view class="item-content">
            <picker 
              class="location-picker"
              mode="region" 
              :value="editForm.location"
              @change="onLocationChange"
            >
              <view class="picker-content">
                <text class="picker-text" :class="{ placeholder: !editForm.location.length }">
                  {{ editForm.location.length ? editForm.location.join(' ') : '请选择所在地' }}
                </text>
                <image src="/static/icons/general/right.png" class="arrow-icon"></image>
              </view>
            </picker>
          </view>
        </view>
      </view>

      <!-- 旅行偏好 -->
      <view class="edit-section">
        <view class="section-label">旅行偏好</view>
        
        <view class="form-item">
          <view class="item-label">喜欢的旅行类型</view>
          <view class="item-content">
            <view class="tags-container">
              <view 
                class="tag" 
                v-for="(tag, index) in travelTypes" 
                :key="index"
                :class="{ active: editForm.preferredTravelTypes.includes(tag) }"
                @tap="toggleTravelType(tag)"
              >
                <text class="tag-text">{{ tag }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="form-item">
          <view class="item-label">常去的目的地</view>
          <view class="item-content">
            <input
              class="item-input"
              type="text"
              placeholder="例如：云南、西藏、日本..."
              placeholder-class="input-placeholder"
              v-model="editForm.frequentDestinations"
              @input="onFormChange"
            />
          </view>
        </view>
      </view>

      <!-- 社交链接 -->
      <view class="edit-section">
        <view class="section-label">社交链接</view>
        
        <view class="form-item">
          <view class="item-label with-icon">
            <image src="/static/icons/general/wechat.png" class="label-icon"></image>
            <text>微信</text>
          </view>
          <view class="item-content">
            <input
              class="item-input"
              type="text"
              placeholder="请输入微信号"
              placeholder-class="input-placeholder"
              v-model="editForm.socialLinks.wechat"
              @input="onFormChange"
            />
          </view>
        </view>

        <view class="form-item">
          <view class="item-label with-icon">
            <image src="/static/icons/general/weibo.png" class="label-icon"></image>
            <text>微博</text>
          </view>
          <view class="item-content">
            <input
              class="item-input"
              type="text"
              placeholder="请输入微博账号"
              placeholder-class="input-placeholder"
              v-model="editForm.socialLinks.weibo"
              @input="onFormChange"
            />
          </view>
        </view>

        <view class="form-item">
          <view class="item-label with-icon">
            <image src="/static/icons/general/douyin.png" class="label-icon"></image>
            <text>抖音</text>
          </view>
          <view class="item-content">
            <input
              class="item-input"
              type="text"
              placeholder="请输入抖音账号"
              placeholder-class="input-placeholder"
              v-model="editForm.socialLinks.douyin"
              @input="onFormChange"
            />
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      originalData: {},
      editForm: {
        id: null,
        avatar: '/static/avatars/touxiang.png',
        nickname: '',
        bio: '',
        gender: '',
        birthday: '',
        phone: '',
        email: '',
        location: [],
        preferredTravelTypes: [],
        frequentDestinations: '',
        socialLinks: {
          wechat: '',
          weibo: '',
          douyin: ''
        }
      },
      genderOptions: ['男', '女', '保密'],
      travelTypes: [
        '自然风光', '城市探索', '美食之旅', '冒险运动',
        '文化历史', '海滨度假', '乡村田园', '摄影采风'
      ],
      hasChanges: false,
      isLoading: false,
      scrollHeight: 0,
      isUploadingAvatar: false,
      BASE_URL: 'http://localhost:8080/api'
    }
  },
  computed: {
    genderIndex() {
      return this.genderOptions.indexOf(this.editForm.gender)
    }
  },
  onLoad() {
    this.initPage()
    this.calculateScrollHeight()
  },
  onShow() {
    this.checkFormChanges()
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
      this.originalData = JSON.parse(JSON.stringify(this.editForm))
      this.isLoading = false
    },
    
    // 加载用户信息 - 修复头像处理
    async loadUserInfo() {
      try {
        const token = uni.getStorageSync('user_token')
        const localUserInfo = uni.getStorageSync('user_info')
        
        if (!localUserInfo || !localUserInfo.id || !token) {
          console.log('未找到用户信息或token')
          this.showError('请先登录')
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/login'
            })
          }, 1500)
          return
        }
        
        console.log('开始加载用户信息，用户ID:', localUserInfo.id)
        
        // 调用后端API获取用户信息
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `${this.BASE_URL}/users/${localUserInfo.id}`,
            method: 'GET',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            success: (res) => {
              console.log('获取用户信息响应:', res)
              resolve(res)
            },
            fail: (err) => {
              console.error('获取用户信息请求失败:', err)
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          const apiUserInfo = res.data.data
          console.log('API返回的用户信息:', apiUserInfo)
          
          // 修复头像处理逻辑 - 与profile.vue保持一致
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
          
          // 处理JSON字段
          let location = []
          let preferredTravelTypes = []
          let socialLinks = {
            wechat: '',
            weibo: '',
            douyin: ''
          }
          
          try {
            if (apiUserInfo.location) {
              location = typeof apiUserInfo.location === 'string' 
                ? JSON.parse(apiUserInfo.location) 
                : apiUserInfo.location
            }
            if (apiUserInfo.preferredTravelTypes) {
              preferredTravelTypes = typeof apiUserInfo.preferredTravelTypes === 'string'
                ? JSON.parse(apiUserInfo.preferredTravelTypes)
                : apiUserInfo.preferredTravelTypes
            }
            if (apiUserInfo.socialLinks) {
              socialLinks = typeof apiUserInfo.socialLinks === 'string'
                ? JSON.parse(apiUserInfo.socialLinks)
                : apiUserInfo.socialLinks
            }
          } catch (e) {
            console.warn('解析用户数据失败:', e)
          }
          
          // 合并用户数据到编辑表单
          this.editForm = {
            ...this.editForm,
            ...apiUserInfo,
            avatar: avatar,
            location,
            preferredTravelTypes,
            socialLinks: {
              ...this.editForm.socialLinks,
              ...socialLinks
            }
          }
          
          console.log('用户信息加载成功，头像:', this.editForm.avatar)
        } else {
          console.warn('获取用户信息API返回异常:', res)
          if (res.statusCode === 400) {
            this.showError('用户不存在，请重新登录')
            uni.removeStorageSync('user_token')
            uni.removeStorageSync('user_info')
            setTimeout(() => {
              uni.navigateTo({
                url: '/pages/login/login'
              })
            }, 1500)
            return
          }
          throw new Error(res.data?.message || '获取用户信息失败')
        }
      } catch (error) {
        console.error('加载用户信息失败:', error)
        const localUserInfo = uni.getStorageSync('user_info')
        if (localUserInfo) {
          this.editForm = {
            ...this.editForm,
            ...localUserInfo
          }
          // 修复本地头像处理 - 与profile.vue保持一致
          if (!this.editForm.avatar || 
              this.editForm.avatar.startsWith('http://tmp/') || 
              (this.editForm.avatar.startsWith('data:image') && this.editForm.avatar.length > 10000)) {
            this.editForm.avatar = '/static/avatars/touxiang.png'
          }
          this.showError('加载失败，使用缓存数据')
        } else {
          this.showError('加载失败，请重新登录')
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/login'
            })
          }, 1500)
        }
      }
    },
    
    // 返回上一页
    goBack() {
      if (this.hasChanges) {
        this.showLeaveConfirm()
      } else {
        uni.navigateBack()
      }
    },
    
    // 显示离开确认
    showLeaveConfirm() {
      uni.showModal({
        title: '提示',
        content: '您有未保存的修改，确定要离开吗？',
        confirmColor: '#b8d4ff',
        success: (res) => {
          if (res.confirm) {
            uni.navigateBack()
          }
        }
      })
    },
    
    // 表单变化处理
    onFormChange() {
      this.checkFormChanges()
    },
    
    // 检查表单变化
    checkFormChanges() {
      this.hasChanges = JSON.stringify(this.editForm) !== JSON.stringify(this.originalData)
    },
    
    // 更换头像
    changeAvatar() {
      if (this.isUploadingAvatar) return
      
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
    
    // 上传头像到服务器 - 修复头像处理逻辑
    async uploadAvatar(tempFilePath) {
      if (this.isUploadingAvatar) return
      
      this.isUploadingAvatar = true
      uni.showLoading({
        title: '上传中...',
        mask: true
      })
      
      try {
        const token = uni.getStorageSync('user_token')
        const userId = this.editForm.id
        
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
          
          // 立即更新头像到服务器 - 与profile.vue保持一致
          await this.updateAvatarToServer(avatarUrl)
          
          // 更新本地表单数据 - 使用完整URL
          const processedAvatarUrl = 'http://localhost:8080' + avatarUrl
          this.editForm.avatar = processedAvatarUrl
          this.onFormChange()
          
          // 更新本地存储
          const updatedUserInfo = { ...this.editForm, avatar: processedAvatarUrl }
          uni.setStorageSync('user_info', updatedUserInfo)
          
          this.showSuccess('头像更新成功')
          
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
    
    // 更新头像URL到服务器 - 新增方法，与profile.vue保持一致
    async updateAvatarToServer(avatarUrl) {
      try {
        const token = uni.getStorageSync('user_token')
        const userId = this.editForm.id
        
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
          console.log('头像更新到服务器成功')
        } else {
          throw new Error(res.data?.message || '更新头像失败')
        }
      } catch (error) {
        console.error('更新头像到服务器失败:', error)
        throw error // 抛出错误让上层处理
      }
    },
    
    // 性别选择
    onGenderChange(e) {
      const index = e.detail.value
      this.editForm.gender = this.genderOptions[index]
      this.onFormChange()
    },
    
    // 生日选择
    onBirthdayChange(e) {
      this.editForm.birthday = e.detail.value
      this.onFormChange()
    },
    
    // 所在地选择
    onLocationChange(e) {
      this.editForm.location = e.detail.value
      this.onFormChange()
    },
    
    // 切换旅行类型
    toggleTravelType(tag) {
      const index = this.editForm.preferredTravelTypes.indexOf(tag)
      if (index > -1) {
        this.editForm.preferredTravelTypes.splice(index, 1)
      } else {
        this.editForm.preferredTravelTypes.push(tag)
      }
      this.onFormChange()
    },
    
    // 保存资料 - 修复头像保存逻辑
    async saveProfile() {
      if (!this.hasChanges || this.isLoading) return
      
      if (!this.validateForm()) {
        return
      }
      
      this.isLoading = true
      
      try {
        const token = uni.getStorageSync('user_token')
        const userId = this.editForm.id
        
        if (!userId || !token) {
          throw new Error('用户未登录')
        }
        
        console.log('开始保存用户信息，用户ID:', userId)
        
        // 准备提交数据
        const submitData = {
          nickname: this.editForm.nickname || '',
          bio: this.editForm.bio || '',
          gender: this.editForm.gender || '',
          birthday: this.editForm.birthday || '',
          phone: this.editForm.phone || '',
          email: this.editForm.email || ''
        }
        
        // 头像已经在选择时立即更新，这里不需要重复提交
        // 如果头像有变化，说明用户选择了新头像但上传失败，需要提示重新上传
        if (this.editForm.avatar !== this.originalData.avatar && 
            this.editForm.avatar.startsWith('/static/')) {
          this.showError('头像上传失败，请重新选择头像')
          return
        }
        
        // 处理JSON字段
        if (this.editForm.location && this.editForm.location.length > 0) {
          submitData.location = JSON.stringify(this.editForm.location)
        }
        
        if (this.editForm.preferredTravelTypes && this.editForm.preferredTravelTypes.length > 0) {
          submitData.preferredTravelTypes = JSON.stringify(this.editForm.preferredTravelTypes)
        }
        
        if (this.editForm.frequentDestinations) {
          submitData.frequentDestinations = this.editForm.frequentDestinations.substring(0, 500)
        }
        
        if (this.editForm.socialLinks) {
          submitData.socialLinks = JSON.stringify(this.editForm.socialLinks)
        }
        
        console.log('提交的数据:', submitData)
        
        // 调用后端API更新用户信息
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `${this.BASE_URL}/users/${userId}`,
            method: 'PUT',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            data: submitData,
            success: (res) => {
              console.log('保存资料响应:', res)
              resolve(res)
            },
            fail: (err) => {
              console.error('保存资料请求失败:', err)
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          // 更新本地存储
          this.updateLocalStorage()
          
          // 更新原始数据
          this.originalData = JSON.parse(JSON.stringify(this.editForm))
          this.hasChanges = false
          
          this.showSuccess('资料更新成功')
          
          // 返回上一页
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          console.warn('保存资料API返回异常:', res)
          if (res.statusCode === 400) {
            const errorDetail = res.data?.message || '未知错误'
            console.error('详细错误信息:', errorDetail)
            
            if (errorDetail.includes('Data too long')) {
              this.showError('数据过长，请简化输入内容')
            } else if (errorDetail.includes('user不存在')) {
              this.showError('用户不存在，请重新登录')
              uni.removeStorageSync('user_token')
              uni.removeStorageSync('user_info')
              setTimeout(() => {
                uni.navigateTo({
                  url: '/pages/login/login'
                })
              }, 1500)
            } else {
              this.showError('保存失败: ' + errorDetail)
            }
            return
          }
          throw new Error(res.data?.message || '更新用户信息失败')
        }
      } catch (error) {
        console.error('保存资料失败:', error)
        this.showError('保存失败: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },
    
    // 表单验证
    validateForm() {
      if (!this.editForm.nickname.trim()) {
        this.showError('请输入昵称')
        return false
      }
      
      if (this.editForm.nickname.trim().length < 2) {
        this.showError('昵称至少2个字符')
        return false
      }
      
      if (this.editForm.phone && !/^1[3-9]\d{9}$/.test(this.editForm.phone)) {
        this.showError('请输入正确的手机号')
        return false
      }
      
      if (this.editForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.editForm.email)) {
        this.showError('请输入正确的邮箱地址')
        return false
      }
      
      return true
    },
    
    // 更新本地存储
    updateLocalStorage() {
      const userData = uni.getStorageSync('user_info') || {}
      const updatedData = {
        ...userData,
        ...this.editForm
      }
      uni.setStorageSync('user_info', updatedData)
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
.profile-edit-page {
  min-height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.nav-bar {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
  position: relative;
}

.nav-left, .nav-right {
  width: 120rpx;
}

.back-icon {
  width: 32rpx;
  height: 32rpx;
}

.nav-title {
  flex: 1;
  text-align: center;
}

.nav-title text {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.save-text {
  font-size: 32rpx;
  color: #b8d4ff;
  font-weight: 500;
}

.save-text.disabled {
  color: #ccc;
}

/* 编辑滚动区域 */
.edit-scroll {
  flex: 1;
  background: #f8f8f8;
}

.edit-section {
  background: #fff;
  margin-bottom: 20rpx;
  padding: 0 30rpx;
}

.section-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  padding: 30rpx 0 20rpx;
  border-bottom: 1rpx solid #f8f8f8;
}

/* 头像编辑 */
.avatar-edit-section {
  position: relative;
  width: 160rpx;
  height: 160rpx;
  margin: 30rpx auto;
  border-radius: 80rpx;
  overflow: hidden;
}

.edit-avatar {
  width: 100%;
  height: 100%;
}

.avatar-edit-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.camera-icon {
  width: 36rpx;
  height: 36rpx;
  margin-bottom: 12rpx;
}

.edit-text {
  font-size: 24rpx;
  color: #fff;
}

/* 表单项目 */
.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f8f8f8;
}

.form-item:last-child {
  border-bottom: none;
}

.item-label {
  width: 200rpx;
  font-size: 28rpx;
  color: #333;
  flex-shrink: 0;
}

.item-label.with-icon {
  display: flex;
  align-items: center;
}

.label-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 12rpx;
}

.item-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.item-input, .item-textarea {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  min-height: 40rpx;
}

.item-textarea {
  height: 120rpx;
  line-height: 1.5;
}

.input-placeholder {
  font-size: 28rpx;
  color: #999;
}

.word-count {
  font-size: 24rpx;
  color: #999;
  margin-left: 20rpx;
  flex-shrink: 0;
}

/* 选择器样式 */
.picker-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.picker-text {
  font-size: 28rpx;
  color: #333;
}

.picker-text.placeholder {
  color: #999;
}

.arrow-icon {
  width: 24rpx;
  height: 24rpx;
  margin-left: 20rpx;
}

/* 标签样式 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.tag {
  padding: 12rpx 24rpx;
  background: #f8f8f8;
  border-radius: 24rpx;
  border: 1rpx solid #eee;
}

.tag.active {
  background: #e8f1ff;
  border-color: #b8d4ff;
}

.tag-text {
  font-size: 24rpx;
  color: #666;
}

.tag.active .tag-text {
  color: #b8d4ff;
  font-weight: 500;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>