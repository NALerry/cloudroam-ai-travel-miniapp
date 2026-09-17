package com.twm.twmbe.controller;

import com.twm.twmbe.entity.Comment;
import com.twm.twmbe.service.CommentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/comments")
@CrossOrigin(origins = "*")
public class CommentController {

    @Autowired
    private CommentService commentService;

    @GetMapping("/post/{postId}")
    public ResponseEntity<Map<String, Object>> getCommentsByPostId(
            @PathVariable Long postId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<Comment> commentsPage = commentService.getCommentsByPostId(postId, page, size);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", commentsPage.getContent());
        response.put("currentPage", page);
        response.put("totalPages", commentsPage.getTotalPages());
        response.put("totalElements", commentsPage.getTotalElements());
        response.put("hasNext", commentsPage.hasNext());

        return ResponseEntity.ok(response);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> createComment(@RequestBody Comment comment) {
        try {
            Comment created = commentService.createComment(comment);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", created);
            response.put("message", "评论发布成功");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "评论发布失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateComment(@PathVariable Long id, @RequestBody Comment comment) {
        try {
            Comment updated = commentService.updateComment(id, comment);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", updated);
            response.put("message", "评论更新成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteComment(@PathVariable Long id) {
        try {
            commentService.deleteComment(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "评论删除成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/{id}/like")
    public ResponseEntity<Map<String, Object>> likeComment(@PathVariable Long id, @RequestBody Map<String, Long> request) {
        try {
            Long userId = request.get("userId");
            commentService.likeComment(id, userId);

            // 获取更新后的评论
            Comment comment = commentService.getCommentById(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", Map.of("likeCount", comment.getLikeCount()));
            response.put("message", "点赞成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PostMapping("/{id}/unlike")
    public ResponseEntity<Map<String, Object>> unlikeComment(@PathVariable Long id, @RequestBody Map<String, Long> request) {
        try {
            Long userId = request.get("userId");
            commentService.unlikeComment(id, userId);

            // 获取更新后的评论
            Comment comment = commentService.getCommentById(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", Map.of("likeCount", comment.getLikeCount()));
            response.put("message", "取消点赞成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/count/{postId}")
    public ResponseEntity<Map<String, Object>> getCommentCount(@PathVariable Long postId) {
        try {
            Long count = commentService.getCommentCountByPostId(postId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", Map.of("count", count));
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "获取评论数量失败");
            return ResponseEntity.badRequest().body(response);
        }
    }
}