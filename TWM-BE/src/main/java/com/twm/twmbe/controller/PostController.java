package com.twm.twmbe.controller;

import com.twm.twmbe.entity.Post;
import com.twm.twmbe.entity.User;
import com.twm.twmbe.service.PostService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/posts")
@CrossOrigin(origins = "*") // 允许跨域
public class PostController {

    @Autowired
    private PostService postService;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getPosts(
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<Post> postsPage = postService.searchPosts(keyword, page, size);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", postsPage.getContent());
        response.put("currentPage", page);
        response.put("totalPages", postsPage.getTotalPages());
        response.put("totalElements", postsPage.getTotalElements());
        response.put("hasNext", postsPage.hasNext());

        return ResponseEntity.ok(response);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> createPost(@RequestBody Post post) {
        try {
            Post created = postService.createPost(post);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", created);
            response.put("message", "发布成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "发布失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getPostById(@PathVariable Long id) {
        try {
            Post post = postService.getPostById(id);

            // 确保作者信息不为空
            if (post.getAuthor() == null) {
                // 设置默认作者信息
                User defaultAuthor = new User();
                defaultAuthor.setId(post.getUserId());
                defaultAuthor.setNickname("匿名用户");
                defaultAuthor.setAvatar("/static/images/default-avatar.png");
                post.setAuthor(defaultAuthor);
            }

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", post);
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.notFound().build();
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updatePost(@PathVariable Long id, @RequestBody Post post) {
        try {
            Post updated = postService.updatePost(id, post);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", updated);
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deletePost(@PathVariable Long id) {
        try {
            postService.deletePost(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "删除成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/{id}/view")
    public ResponseEntity<Map<String, Object>> incrementViewCount(@PathVariable Long id) {
        try {
            postService.incrementViewCount(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "浏览计数增加成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/{id}/like")
    public ResponseEntity<Map<String, Object>> likePost(@PathVariable Long id, @RequestBody Map<String, Long> request) {
        try {
            Long userId = request.get("userId");
            postService.toggleLike(id, userId);

            // 获取更新后的帖子信息（包含作者信息）
            Post post = postService.getPostById(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", Map.of("likeCount", post.getLikeCount()));
            response.put("message", "点赞成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<Map<String, Object>> getUserPosts(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<Post> postsPage = postService.getUserPosts(userId, page, size);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", postsPage.getContent());
        response.put("currentPage", page);
        response.put("totalPages", postsPage.getTotalPages());
        response.put("totalElements", postsPage.getTotalElements());

        return ResponseEntity.ok(response);
    }
}