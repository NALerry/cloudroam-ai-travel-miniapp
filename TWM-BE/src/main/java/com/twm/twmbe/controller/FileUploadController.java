package com.twm.twmbe.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/upload")
@CrossOrigin(origins = "*")
public class FileUploadController {

    @Value("${file.upload-dir:uploads}")
    private String uploadDir;

    @PostMapping("/avatar")
    public ResponseEntity<Map<String, Object>> uploadAvatar(@RequestParam("file") MultipartFile file,
                                                            @RequestParam("userId") Long userId) {
        try {
            // 检查文件类型
            String contentType = file.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "只能上传图片文件");
                return ResponseEntity.badRequest().body(response);
            }

            // 检查文件大小（限制为5MB）
            if (file.getSize() > 5 * 1024 * 1024) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "图片大小不能超过5MB");
                return ResponseEntity.badRequest().body(response);
            }

            // 创建上传目录
            File dir = new File(uploadDir + File.separator + "avatars");
            if (!dir.exists()) {
                dir.mkdirs();
            }

            // 生成唯一文件名
            String originalFilename = file.getOriginalFilename();
            String fileExtension = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String filename = "avatar_" + userId + "_" + UUID.randomUUID() + fileExtension;

            // 保存文件
            Path filePath = Paths.get(dir.getAbsolutePath(), filename);
            Files.copy(file.getInputStream(), filePath);

            // 生成访问URL - 修复：使用正确的URL路径
            String fileUrl = "/uploads/avatars/" + filename;

            System.out.println("头像上传成功: " + fileUrl);
            System.out.println("文件保存路径: " + filePath.toString());

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("url", fileUrl);
            response.put("message", "头像上传成功");

            return ResponseEntity.ok(response);

        } catch (IOException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "文件上传失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "上传失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    // 新增：帖子图片上传
    @PostMapping("/post")
    public ResponseEntity<Map<String, Object>> uploadPostImage(@RequestParam("file") MultipartFile file) {
        try {
            // 检查文件类型
            String contentType = file.getContentType();
            if (contentType == null || !contentType.startsWith("image/")) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "只能上传图片文件");
                return ResponseEntity.badRequest().body(response);
            }

            // 检查文件大小（限制为10MB）
            if (file.getSize() > 10 * 1024 * 1024) {
                Map<String, Object> response = new HashMap<>();
                response.put("success", false);
                response.put("message", "图片大小不能超过10MB");
                return ResponseEntity.badRequest().body(response);
            }

            // 创建上传目录
            File dir = new File(uploadDir + File.separator + "posts");
            if (!dir.exists()) {
                dir.mkdirs();
            }

            // 生成唯一文件名
            String originalFilename = file.getOriginalFilename();
            String fileExtension = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String filename = "post_" + UUID.randomUUID() + fileExtension;

            // 保存文件
            Path filePath = Paths.get(dir.getAbsolutePath(), filename);
            Files.copy(file.getInputStream(), filePath);

            // 生成访问URL
            String fileUrl = "/uploads/posts/" + filename;

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("url", fileUrl);
            response.put("message", "图片上传成功");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "上传失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }
}