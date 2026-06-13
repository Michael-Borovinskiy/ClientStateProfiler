package com.boro.apps.usersrvc.controllers;


import com.boro.apps.usersrvc.domain.UserRequestBody;
import com.boro.apps.usersrvc.exceptions.UserAlreadyExistException;
import com.boro.apps.usersrvc.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import reactor.core.publisher.Mono;

@Controller
@RequiredArgsConstructor
public class IndexController {

    private final UserService userService;

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @GetMapping("/user_exist")
    public String user_exist() {
        return "user_exist";
    }

    @PostMapping(value = "/users/v1/users")
    public Mono<String> signUp(UserRequestBody userRequestBody) throws UserAlreadyExistException {
        return userService.signUp(userRequestBody).map(saved -> {
            if (saved.equals("user_exist")) {
                return "redirect:/user_exist";
            }
            return "redirect:/login";
        });
    }

}
