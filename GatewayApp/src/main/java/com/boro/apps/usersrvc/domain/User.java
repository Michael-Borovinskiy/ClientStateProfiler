package com.boro.apps.usersrvc.domain;

import lombok.*;

import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;


@AllArgsConstructor
@NoArgsConstructor
@Builder
@Data
@Table(name = "USERS")
public class User implements UserDetails {

    @Id
    private Long id;

    private String login;

    private String password;

    @Column("granted_authority")
    private String grantedAuthority;

    public Long getId() {
        return id;
    }

    public String getLogin() {
        return login;
    }

    public String getPassword() {
        return password;
    }

    public String getGrantedAuthority() {
        return grantedAuthority;
    }


    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of((GrantedAuthority) this::getGrantedAuthority);
    }

    @Override
    public String getUsername() {
        return login;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    @Override
    public boolean isEnabled() {
        return true;
    }

    public User(String name, String password, String grantedAuthority) {
        this.login = name;
        this.password = password;
        this.grantedAuthority = grantedAuthority;
    }

    public UserDto toDto() {
        return new UserDto(this.getId(), this.getLogin(), this.getGrantedAuthority());
    }
}