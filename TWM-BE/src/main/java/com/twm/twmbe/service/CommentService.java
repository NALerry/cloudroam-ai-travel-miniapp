package com.twm.twmbe.service;

import com.twm.twmbe.entity.Comment;
import org.springframework.data.domain.Page;

public interface CommentService {
    Page<Comment> getCommentsByPostId(Long postId, int page, int size);
    Comment createComment(Comment comment);
    Comment updateComment(Long id, Comment comment);
    void deleteComment(Long id);
    void likeComment(Long commentId, Long userId);
    void unlikeComment(Long commentId, Long userId);
    Comment getCommentById(Long id);
    Long getCommentCountByPostId(Long postId);
}