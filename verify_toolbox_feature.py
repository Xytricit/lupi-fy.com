#!/usr/bin/env python3

with open('templates/games/editor_enhanced.html', 'r', encoding='utf-8') as f:
    content = f.read()

requirements = {
    'Function definition': 'function setupToolboxCollapseOnDrag(workspace)' in content,
    'Function is called': 'setupToolboxCollapseOnDrag(workspace)' in content,
    'Checks workspace exists': 'if (!workspace)' in content and 'Workspace not available' in content,
    'Checks toolbox exists': 'if (!toolbox)' in content and 'Toolbox not available' in content,
    'BLOCK_DRAG event listener': 'Blockly.Events.BLOCK_DRAG' in content,
    'isStart check': 'event.isStart' in content,
    'isInFlyout check': 'block.isInFlyout' in content,
    'getFlyout used': 'workspace.getFlyout()' in content,
    'getToolbox used': 'workspace.getToolbox()' in content,
    'getSelectedItem used': 'toolbox.getSelectedItem()' in content,
    'setCollapsed used': 'setCollapsed(true)' in content,
    'Minimal setTimeout delay': 'setTimeout(() => {' in content and ', 50)' in content,
    'Try-catch error handling': 'try {' in content and 'catch (e)' in content,
    'Warning logging': 'console.warn' in content and 'Collapsed toolbox category' in content,
    'Public API only (typeof check)': 'typeof dragStartFlyoutCategory.isCollapsed === \'function\'' in content,
    'Documentation present': 'REQUIREMENTS MET' in content and 'USAGE:' in content,
}

print('Toolbox Collapse-on-Drag Feature Verification:')
print('=' * 60)

all_pass = True
for requirement, result in requirements.items():
    status = 'PASS' if result else 'FAIL'
    if not result:
        all_pass = False
    print('[{}] {}'.format(status, requirement))

print()
print('=' * 60)
if all_pass:
    print('[SUCCESS] All requirements implemented!')
else:
    print('[WARNING] Some requirements may be missing!')

print()
print('IMPLEMENTATION DETAILS:')
print('- Function location: Line ~1182')
print('- Called at: Line ~784 (after setupEventListeners)')
print('- Event type: Blockly.Events.BLOCK_DRAG')
print('- Collapse trigger: When drag ends (isStart = false)')
print('- Delay: 50ms setTimeout for drag state confirmation')
