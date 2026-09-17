// utils/date.js

/**
 * 安全解析日期字符串（兼容 iOS）
 * @param {string} dateStr 日期字符串
 * @returns {Date} 日期对象
 */
export function safeParseDate(dateStr) {
  if (!dateStr) return new Date()
  
  // 尝试直接解析
  let date = new Date(dateStr)
  
  if (isNaN(date.getTime())) {
    // 尝试替换空格为 T（ISO 格式）
    date = new Date(dateStr.replace(' ', 'T') + ':00')
  }
  
  if (isNaN(date.getTime())) {
    // 尝试手动解析常见格式
    const patterns = [
      /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$/, // YYYY-MM-DD HH:mm
      /^(\d{4})-(\d{2})-(\d{2})$/, // YYYY-MM-DD
      /^(\d{4})\/(\d{2})\/(\d{2}) (\d{2}):(\d{2})$/, // YYYY/MM/DD HH:mm
      /^(\d{4})\/(\d{2})\/(\d{2})$/, // YYYY/MM/DD
    ]
    
    for (const pattern of patterns) {
      const match = dateStr.match(pattern)
      if (match) {
        const [, year, month, day, hour = 0, minute = 0] = match
        date = new Date(
          parseInt(year),
          parseInt(month) - 1,
          parseInt(day),
          parseInt(hour),
          parseInt(minute)
        )
        break
      }
    }
  }
  
  // 如果仍然无效，返回当前日期
  if (isNaN(date.getTime())) {
    console.warn('无法解析日期:', dateStr)
    return new Date()
  }
  
  return date
}

/**
 * 格式化相对时间
 * @param {string} timeStr 时间字符串
 * @returns {string} 相对时间描述
 */
export function formatRelativeTime(timeStr) {
  const date = safeParseDate(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60 * 1000) {
    return '刚刚'
  } else if (diff < 60 * 60 * 1000) {
    return Math.floor(diff / (60 * 1000)) + '分钟前'
  } else if (diff < 24 * 60 * 60 * 1000) {
    return Math.floor(diff / (60 * 60 * 1000)) + '小时前'
  } else if (diff < 30 * 24 * 60 * 60 * 1000) {
    return Math.floor(diff / (24 * 60 * 60 * 1000)) + '天前'
  } else {
    return date.getFullYear() + '年' + (date.getMonth() + 1) + '月' + date.getDate() + '日'
  }
}

/**
 * 格式化日期为 YYYY-MM-DD
 * @param {string} dateStr 日期字符串
 * @returns {string} 格式化后的日期
 */
export function formatDate(dateStr) {
  const date = safeParseDate(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 格式化日期时间为 YYYY-MM-DD HH:mm
 * @param {string} dateStr 日期字符串
 * @returns {string} 格式化后的日期时间
 */
export function formatDateTime(dateStr) {
  const date = safeParseDate(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}