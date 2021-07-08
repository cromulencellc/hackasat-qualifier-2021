####
# F prime CMakeLists.txt:
#
# SOURCE_FILES: combined list of source and autocoding diles
# MOD_DEPS: (optional) module dependencies
#
####

message(STATUS "Flag Code for this build: ${FLAG_CODE_INPUT}")
add_definitions( -DFLAG_CODE="${FLAG_CODE_INPUT}" )

set(SOURCE_FILES
  "${CMAKE_CURRENT_LIST_DIR}/FlagSvrComponentAi.xml"
  "${CMAKE_CURRENT_LIST_DIR}/FlagSvrComponentImpl.cpp"
)
register_fprime_module()
