package com.boro.apps.usersrvc.controllers;


import com.boro.apps.usersrvc.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * @author Michael-Borovinskiy
 * 28.08.2024
 */
@RequiredArgsConstructor
@Controller
@RequestMapping("/users/v1")
public class AboutMeController {

    @Autowired
    private final UserService userService;

    @GetMapping("/user_authorities")
    public String getUserAuthorities(Model model){
        model.addAttribute("selfinfo",userService.getUserAuthorities());
        return "selfinfo";
    }

}