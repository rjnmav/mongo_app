#!/usr/bin/env python3
"""
Style validation script for MongoDB Visualizer.

This script validates that all the modern styling components
are properly implemented and can be imported without errors.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_style_imports():
    """Test that all style modules can be imported."""
    print("🧪 Testing Style Module Imports...")
    
    try:
        from src.styles.modern_styles import ModernStyles
        print("✅ ModernStyles imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ModernStyles: {e}")
        return False
    
    try:
        from src.styles.theme_manager import theme_manager, ThemeType
        print("✅ ThemeManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ThemeManager: {e}")
        return False
    
    return True

def test_style_generation():
    """Test that styles can be generated."""
    print("\n🎨 Testing Style Generation...")
    
    try:
        from src.styles.modern_styles import ModernStyles
        
        # Test individual style components
        components = [
            ("Main Window", ModernStyles.get_main_window_style),
            ("Menu Bar", ModernStyles.get_menu_bar_style),
            ("Tool Bar", ModernStyles.get_tool_bar_style),
            ("Status Bar", ModernStyles.get_status_bar_style),
            ("Tree Widget", ModernStyles.get_tree_widget_style),
            ("Buttons", ModernStyles.get_button_style),
            ("Input Controls", ModernStyles.get_input_style),
            ("Dialogs", ModernStyles.get_dialog_style),
            ("Tables", ModernStyles.get_table_style),
            ("Tab Widget", ModernStyles.get_tab_widget_style),
            ("Splitters", ModernStyles.get_splitter_style),
            ("Scroll Bars", ModernStyles.get_scroll_bar_style),
        ]
        
        for name, style_func in components:
            try:
                style = style_func()
                if style and len(style) > 10:  # Basic validation
                    print(f"✅ {name} styles generated ({len(style)} characters)")
                else:
                    print(f"⚠️  {name} styles seem too short")
            except Exception as e:
                print(f"❌ Failed to generate {name} styles: {e}")
                return False
        
        # Test complete stylesheet
        complete_style = ModernStyles.get_complete_stylesheet()
        print(f"✅ Complete stylesheet generated ({len(complete_style)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Style generation failed: {e}")
        return False

def test_theme_functionality():
    """Test theme switching functionality."""
    print("\n🌈 Testing Theme Functionality...")
    
    try:
        from src.styles.theme_manager import theme_manager, ThemeType
        
        # Test theme enumeration
        themes = theme_manager.get_theme_names()
        print(f"✅ Available themes: {', '.join(themes)}")
        
        # Test current theme
        current = theme_manager.get_current_theme()
        print(f"✅ Current theme: {current.value}")
        
        # Test theme switching
        for theme in ThemeType:
            try:
                theme_manager.set_theme(theme)
                print(f"✅ Successfully switched to {theme.value} theme")
            except Exception as e:
                print(f"❌ Failed to switch to {theme.value}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Theme functionality test failed: {e}")
        return False

def test_color_schemes():
    """Test that all color schemes are properly defined."""
    print("\n🎯 Testing Color Schemes...")
    
    try:
        from src.styles.theme_manager import theme_manager, ThemeType
        from src.styles.modern_styles import ModernStyles
        
        required_colors = [
            'primary', 'primary_light', 'primary_dark',
            'secondary', 'secondary_light', 'secondary_dark',
            'success', 'warning', 'error', 'info',
            'background', 'surface', 'on_background', 'on_surface',
            'border', 'border_dark', 'text_primary', 'text_secondary',
            'text_disabled', 'hover', 'selection', 'shadow'
        ]
        
        for theme in ThemeType:
            theme_manager.set_theme(theme)
            print(f"\n🎨 Validating {theme.value} theme:")
            
            missing_colors = []
            for color in required_colors:
                if color in ModernStyles.COLORS:
                    color_value = ModernStyles.COLORS[color]
                    if color_value and (color_value.startswith('#') or color_value.startswith('rgba')):
                        print(f"  ✅ {color}: {color_value}")
                    else:
                        print(f"  ⚠️  {color}: {color_value} (unusual format)")
                else:
                    missing_colors.append(color)
            
            if missing_colors:
                print(f"  ❌ Missing colors: {', '.join(missing_colors)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Color scheme test failed: {e}")
        return False

def show_style_preview():
    """Show a preview of the styling system capabilities."""
    print("\n🖼️  Style System Preview")
    print("=" * 50)
    
    from src.styles.modern_styles import ModernStyles
    from src.styles.theme_manager import theme_manager, ThemeType
    
    print(f"""
📱 Modern MongoDB Visualizer Styling System

🎨 Features:
   • Material Design inspired interface
   • 4 beautiful themes (Light, Dark, Blue, Green)
   • Professional color schemes
   • Modern typography and spacing
   • Card-based layouts with shadow effects
   • Responsive hover states and transitions
   • Consistent design language

🌈 Current Theme: {theme_manager.get_current_theme().value.title()}
   Primary Color: {ModernStyles.COLORS['primary']}
   Background: {ModernStyles.COLORS['background']}
   Surface: {ModernStyles.COLORS['surface']}
   Text: {ModernStyles.COLORS['text_primary']}

🛠️  Styled Components:
   ✅ Main window and layouts
   ✅ Menu bars and toolbars
   ✅ Database tree views
   ✅ Document viewer cards
   ✅ Connection dialogs
   ✅ Form controls (buttons, inputs, dropdowns)
   ✅ Data tables and grids
   ✅ Progress indicators
   ✅ Status bars and splitters
   ✅ Scroll bars and tooltips

🚀 Usage:
   • Run main app: python app.py
   • Change themes via View → Themes menu
   • Styles applied automatically on startup
   • No configuration required
    """)

def main():
    """Run all style validation tests."""
    print("🎨 MongoDB Visualizer - Modern Styling Validation")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_style_imports),
        ("Style Generation", test_style_generation),
        ("Theme Functionality", test_theme_functionality),
        ("Color Schemes", test_color_schemes),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'='*20} {name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED")
    
    print(f"\n{'='*60}")
    print(f"🏆 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All styling tests passed! The modern styling system is ready.")
        show_style_preview()
        return 0
    else:
        print("❌ Some tests failed. Please check the styling implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
