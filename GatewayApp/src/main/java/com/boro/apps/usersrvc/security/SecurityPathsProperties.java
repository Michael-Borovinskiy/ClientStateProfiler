package com.boro.apps.usersrvc.security;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * @author Michael-Borovinskiy
 * 18.04.2026
 */
@Component
@ConfigurationProperties(prefix = "security.paths")
public class SecurityPathsProperties {
    private List<String> publicGet = new ArrayList<>();
    private List<String> publicPost = new ArrayList<>();
    private List<String> authenticatedGet = new ArrayList<>();
    private List<String> adminGet = new ArrayList<>();
    private List<String> monitoringGet = new ArrayList<>();
    private List<String> monitoringPost = new ArrayList<>();

    public List<String> getPublicGet() {
        return publicGet;
    }

    public void setPublicGet(List<String> publicGet) {
        this.publicGet = publicGet;
    }

    public List<String> getPublicPost() {
        return publicPost;
    }

    public void setPublicPost(List<String> publicPost) {
        this.publicPost = publicPost;
    }

    public List<String> getAuthenticatedGet() {
        return authenticatedGet;
    }

    public void setAuthenticatedGet(List<String> authenticatedGet) {
        this.authenticatedGet = authenticatedGet;
    }

    public List<String> getAdminGet() {
        return adminGet;
    }

    public void setAdminGet(List<String> adminGet) {
        this.adminGet = adminGet;
    }

    public List<String> getMonitoringGet() {
        return monitoringGet;
    }

    public void setMonitoringGet(List<String> monitoringGet) {
        this.monitoringGet = monitoringGet;
    }

    public List<String> getMonitoringPost() {
        return monitoringPost;
    }

    public void setMonitoringWrite(List<String> monitoringPost) {
        this.monitoringPost = monitoringPost;
    }
}
