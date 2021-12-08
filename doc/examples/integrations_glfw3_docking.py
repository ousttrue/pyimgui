# -*- coding: utf-8 -*-
import pathlib
import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer
from testwindow import show_test_window


HERE = pathlib.Path(__file__).absolute().parent


def docking_space(name: str):
    flags = (imgui.WINDOW_MENU_BAR
             | imgui.WINDOW_NO_DOCKING
             # | imgui.WINDOW_NO_BACKGROUND
             | imgui.WINDOW_NO_TITLE_BAR
             | imgui.WINDOW_NO_COLLAPSE
             | imgui.WINDOW_NO_RESIZE
             | imgui.WINDOW_NO_MOVE
             | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS
             | imgui.WINDOW_NO_NAV_FOCUS
             )

    viewport = imgui.get_main_viewport()
    x, y = viewport.pos
    w, h = viewport.size
    imgui.set_next_window_position(x, y)
    imgui.set_next_window_size(w, h)
    # imgui.set_next_window_viewport(viewport.id)
    imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0)
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.0)

    # When using ImGuiDockNodeFlags_PassthruCentralNode, DockSpace() will render our background and handle the pass-thru hole, so we ask Begin() to not render a background.
    # local window_flags = self.window_flags
    # if bit.band(self.dockspace_flags, ) ~= 0 then
    #     window_flags = bit.bor(window_flags, const.ImGuiWindowFlags_.NoBackground)
    # end

    # Important: note that we proceed even if Begin() returns false (aka window is collapsed).
    # This is because we want to keep our DockSpace() active. If a DockSpace() is inactive,
    # all active windows docked into it will lose their parent and become undocked.
    # We cannot preserve the docking relationship between an active window and an inactive docking, otherwise
    # any change of dockspace/settings would lead to windows being stuck in limbo and never being visible.
    imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))
    imgui.begin(name, None, flags)
    imgui.pop_style_var()
    imgui.pop_style_var(2)

    # DockSpace
    dockspace_id = imgui.get_id(name)
    imgui.dockspace(dockspace_id, (0, 0), imgui.DOCKNODE_PASSTHRU_CENTRAL_NODE)

    imgui.end()


def load_font(path: pathlib.Path):
    '''
    https://github.com/ocornut/imgui/blob/master/docs/FONTS.md#font-loading-instructions
    '''
    io = imgui.get_io()
    # Load a first font
    fonts = io.fonts
    fonts.add_font_default()

    # Add character ranges and merge into the previous font
    # The ranges array is not copied by the AddFont* functions and is used lazily
    # so ensure it is available at the time of building or calling GetTexDataAsRGBA32().
    # Will not be copied by AddFont* so keep in scope.
    config = imgui.core._FontConfig()
    config.merge_mode = True
    config.glyph_min_advance_x = 13.0
    # fonts->AddFontFromFileTTF("DroidSans.ttf", 18.0f, &config, io.Fonts->GetGlyphRangesJapanese()); // Merge into first font

    import ctypes
    icons_ranges = (ctypes.c_ushort * 3)(0xf000, 0xf3ff, 0)
    address = ctypes.addressof(icons_ranges)

    fonts.add_font_from_file_ttf(
        str(path), 18.0,
        config,
        imgui.core._StaticGlyphRanges.from_address(address))
    # Merge into first font
    fonts.build()


def main():
    imgui.create_context()
    io = imgui.get_io()
    io.config_flags |= imgui.CONFIG_DOCKING_ENABLE

    # 4.7
    # from https://github.com/FortAwesome/Font-Awesome/blob/a8386aae19e200ddb0f6845b5feeee5eb7013687/fonts/fontawesome-webfont.ttf
    load_font(HERE / "fontawesome-webfont.ttf")

    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    show_custom_window = True

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        docking_space('docking_space')

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        if show_custom_window:
            is_expand, show_custom_window = imgui.begin("Custom window", True)
            if is_expand:
                imgui.text("Bar")
                imgui.text_ansi("B\033[31marA\033[mnsi ")
                imgui.text_ansi_colored("Eg\033[31mgAn\033[msi ", 0.2, 1., 0.)
                imgui.extra.text_ansi_colored("Eggs", 0.2, 1., 0.)
            imgui.end()

        imgui.show_metrics_window(True)

        imgui.begin('font')
        ICON_FA_SEARCH = b"\xef\x80\x82".decode('utf-8')
        imgui.text_unformatted(ICON_FA_SEARCH)
        imgui.end()

        show_test_window()
        # imgui.show_test_window()

        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


if __name__ == "__main__":
    main()
