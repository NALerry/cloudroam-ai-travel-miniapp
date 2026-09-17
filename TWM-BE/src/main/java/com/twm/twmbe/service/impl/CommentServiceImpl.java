package com.twm.twmbe.service.impl;

import com.twm.twmbe.entity.Comment;
import com.twm.twmbe.repository.CommentRepository;
import com.twm.twmbe.repository.PostRepository;
import com.twm.twmbe.service.CommentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class CommentServiceImpl implements CommentService {

    private final CommentRepository commentRepository;

    @Autowired
    private PostRepository postRepository;

    @Autowired
    public CommentServiceImpl(CommentRepository commentRepository) {
        this.commentRepository = commentRepository;
    }

    @Override
    public Page<Comment> getCommentsByPostId(Long postId, int page, int size) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("createdAt").descending());
        return commentRepository.findByPostIdOrderByCreatedAtDesc(postId, pageable);
    }

    @Override
    @Transactional
    public Comment createComment(Comment comment) {
        comment.setCreatedAt(LocalDateTime.now());
        comment.setUpdatedAt(LocalDateTime.now());

        if (comment.getLikeCount() == null) {
            comment.setLikeCount(0);
        }

        Comment savedComment = commentRepository.save(comment);

        // 更新帖子的评论计数
        try {
            postRepository.incrementCommentCount(comment.getPostId());
        } catch (Exception e) {
            // 记录错误但不中断流程
            System.err.println("更新帖子评论计数失败: " + e.getMessage());
        }

        return savedComment;
    }

    @Override
    @Transactional
    public Comment updateComment(Long id, Comment comment) {
        Comment existing = commentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("评论不存在，ID: " + id));

        if (comment.getContent() != null) {
            existing.setContent(comment.getContent());
        }

        existing.setUpdatedAt(LocalDateTime.now());
        return commentRepository.save(existing);
    }

    @Override
    @Transactional
    public void deleteComment(Long id) {
        Comment comment = commentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("评论不存在，ID: " + id));

        Long postId = comment.getPostId();
        commentRepository.deleteById(id);

        // 更新帖子的评论计数
        try {
            postRepository.decrementCommentCount(postId);
        } catch (Exception e) {
            // 记录错误但不中断流程
            System.err.println("更新帖子评论计数失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional
    public void likeComment(Long commentId, Long userId) {
        Comment comment = commentRepository.findById(commentId)
                .orElseThrow(() -> new RuntimeException("评论不存在，ID: " + commentId));

        // 这里简化处理，实际应该维护一个点赞表来记录用户点赞状态
        comment.setLikeCount(comment.getLikeCount() + 1);
        commentRepository.save(comment);
    }

    @Override
    @Transactional
    public void unlikeComment(Long commentId, Long userId) {
        Comment comment = commentRepository.findById(commentId)
                .orElseThrow(() -> new RuntimeException("评论不存在，ID: " + commentId));

        comment.setLikeCount(Math.max(0, comment.getLikeCount() - 1));
        commentRepository.save(comment);
    }

    @Override
    public Comment getCommentById(Long id) {
        return commentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("评论不存在，ID: " + id));
    }

    @Override
    public Long getCommentCountByPostId(Long postId) {
        return commentRepository.countByPostId(postId);
    }
}