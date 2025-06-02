"""
Main GUI window for the Moveworks Compound Action Wizard.

This module provides a tkinter-based graphical interface for creating
Compound Actions with enhanced user experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional, Dict, Any
import json
from pathlib import Path

from ..models.base import CompoundAction
from ..serializers import serialize_compound_action
from ..templates.template_library import template_library
from ..ai.action_suggester import action_suggester
from ..bender.bender_assistant import bender_assistant


class MoveworksWizardGUI:
    """
    Main GUI application for the Moveworks Compound Action Wizard.
    
    Provides a user-friendly interface for creating Compound Actions
    with templates, AI suggestions, and Bender assistance.
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Moveworks Compound Action Wizard")
        self.root.geometry("1200x800")
        
        # Current compound action being edited
        self.compound_action: Optional[CompoundAction] = None
        
        # Setup the UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the main user interface."""
        # Create main menu
        self._create_menu()
        
        # Create main layout
        self._create_main_layout()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new_compound_action)
        file_menu.add_command(label="Open Template", command=self._open_template)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save_compound_action)
        file_menu.add_command(label="Save As...", command=self._save_as_compound_action)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="AI Suggestions", command=self._show_ai_suggestions)
        tools_menu.add_command(label="Bender Assistant", command=self._show_bender_assistant)
        tools_menu.add_command(label="Template Library", command=self._show_template_library)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create the main application layout."""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Project tree and tools
        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Main editor
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)
        
        # Setup left panel
        self._setup_left_panel(left_frame)
        
        # Setup right panel
        self._setup_right_panel(right_frame)
    
    def _setup_left_panel(self, parent):
        """Setup the left panel with tools and navigation."""
        # Quick Start section
        quick_start_frame = ttk.LabelFrame(parent, text="Quick Start", padding=10)
        quick_start_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(quick_start_frame, text="New Compound Action", 
                  command=self._new_compound_action).pack(fill=tk.X, pady=2)
        ttk.Button(quick_start_frame, text="Browse Templates", 
                  command=self._show_template_library).pack(fill=tk.X, pady=2)
        ttk.Button(quick_start_frame, text="AI Suggestions", 
                  command=self._show_ai_suggestions).pack(fill=tk.X, pady=2)
        
        # AI Assistant section
        ai_frame = ttk.LabelFrame(parent, text="AI Assistant", padding=10)
        ai_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ai_frame, text="Describe what you want to do:").pack(anchor=tk.W)
        self.ai_description = tk.Text(ai_frame, height=3, wrap=tk.WORD)
        self.ai_description.pack(fill=tk.X, pady=2)
        
        ttk.Button(ai_frame, text="Get Suggestions", 
                  command=self._get_ai_suggestions).pack(fill=tk.X, pady=2)
        
        # Current Action Overview
        overview_frame = ttk.LabelFrame(parent, text="Current Action", padding=10)
        overview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.overview_text = scrolledtext.ScrolledText(overview_frame, height=10, 
                                                      state=tk.DISABLED, wrap=tk.WORD)
        self.overview_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_right_panel(self, parent):
        """Setup the right panel with the main editor."""
        # Create notebook for different tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Basic Info tab
        self._create_basic_info_tab()
        
        # Steps tab
        self._create_steps_tab()
        
        # YAML Preview tab
        self._create_yaml_preview_tab()
    
    def _create_basic_info_tab(self):
        """Create the basic information tab."""
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Basic Info")
        
        # Compound Action Name
        ttk.Label(basic_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(basic_frame, width=50)
        self.name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Description
        ttk.Label(basic_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_text = tk.Text(basic_frame, height=3, width=50, wrap=tk.WORD)
        self.description_text.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Input Arguments section
        input_args_frame = ttk.LabelFrame(basic_frame, text="Input Arguments", padding=10)
        input_args_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, 
                             padx=5, pady=10)
        
        # Input arguments list
        self.input_args_tree = ttk.Treeview(input_args_frame, columns=('Value',), height=6)
        self.input_args_tree.heading('#0', text='Argument Name')
        self.input_args_tree.heading('Value', text='Value/Expression')
        self.input_args_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons for input arguments
        args_buttons_frame = ttk.Frame(input_args_frame)
        args_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(args_buttons_frame, text="Add Argument", 
                  command=self._add_input_argument).pack(side=tk.LEFT, padx=2)
        ttk.Button(args_buttons_frame, text="Edit Argument", 
                  command=self._edit_input_argument).pack(side=tk.LEFT, padx=2)
        ttk.Button(args_buttons_frame, text="Remove Argument", 
                  command=self._remove_input_argument).pack(side=tk.LEFT, padx=2)
        ttk.Button(args_buttons_frame, text="Bender Help", 
                  command=self._show_bender_assistant).pack(side=tk.RIGHT, padx=2)
        
        # Configure grid weights
        basic_frame.columnconfigure(1, weight=1)
        basic_frame.rowconfigure(2, weight=1)
    
    def _create_steps_tab(self):
        """Create the steps editor tab."""
        steps_frame = ttk.Frame(self.notebook)
        self.notebook.add(steps_frame, text="Steps")
        
        # Steps list
        self.steps_tree = ttk.Treeview(steps_frame, columns=('Type', 'Details'), height=15)
        self.steps_tree.heading('#0', text='Step')
        self.steps_tree.heading('Type', text='Type')
        self.steps_tree.heading('Details', text='Details')
        self.steps_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons for steps
        steps_buttons_frame = ttk.Frame(steps_frame)
        steps_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(steps_buttons_frame, text="Add Step", 
                  command=self._add_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(steps_buttons_frame, text="Edit Step", 
                  command=self._edit_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(steps_buttons_frame, text="Remove Step", 
                  command=self._remove_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(steps_buttons_frame, text="Move Up", 
                  command=self._move_step_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(steps_buttons_frame, text="Move Down", 
                  command=self._move_step_down).pack(side=tk.LEFT, padx=2)
    
    def _create_yaml_preview_tab(self):
        """Create the YAML preview tab."""
        yaml_frame = ttk.Frame(self.notebook)
        self.notebook.add(yaml_frame, text="YAML Preview")
        
        # YAML text area
        self.yaml_text = scrolledtext.ScrolledText(yaml_frame, wrap=tk.NONE, 
                                                  font=('Courier', 10))
        self.yaml_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons for YAML
        yaml_buttons_frame = ttk.Frame(yaml_frame)
        yaml_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(yaml_buttons_frame, text="Refresh Preview", 
                  command=self._refresh_yaml_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(yaml_buttons_frame, text="Copy to Clipboard", 
                  command=self._copy_yaml_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(yaml_buttons_frame, text="Save YAML", 
                  command=self._save_compound_action).pack(side=tk.RIGHT, padx=2)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _new_compound_action(self):
        """Create a new compound action."""
        self.compound_action = CompoundAction(
            name="New Compound Action",
            description="",
            input_args={},
            steps=[]
        )
        self._update_ui()
        self._set_status("New compound action created")
    
    def _open_template(self):
        """Open a template selection dialog."""
        self._show_template_library()
    
    def _save_compound_action(self):
        """Save the current compound action."""
        if not self.compound_action:
            messagebox.showwarning("Warning", "No compound action to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                yaml_content = serialize_compound_action(self.compound_action)
                with open(filename, 'w') as f:
                    f.write(yaml_content)
                self._set_status(f"Saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def _save_as_compound_action(self):
        """Save the compound action with a new name."""
        self._save_compound_action()
    
    def _show_ai_suggestions(self):
        """Show the AI suggestions dialog."""
        # This would open a dialog for AI suggestions
        messagebox.showinfo("AI Suggestions", "AI Suggestions dialog would open here")
    
    def _show_bender_assistant(self):
        """Show the Bender assistant dialog."""
        # This would open a dialog for Bender assistance
        messagebox.showinfo("Bender Assistant", "Bender Assistant dialog would open here")
    
    def _show_template_library(self):
        """Show the template library dialog."""
        # This would open a dialog for template selection
        messagebox.showinfo("Template Library", "Template Library dialog would open here")
    
    def _show_about(self):
        """Show the about dialog."""
        messagebox.showinfo("About", 
                           "Moveworks Compound Action Wizard\n"
                           "Phase 4: Advanced Features & UI Enhancement\n\n"
                           "Create Compound Actions for Moveworks Action Activities")
    
    def _get_ai_suggestions(self):
        """Get AI suggestions based on user description."""
        description = self.ai_description.get("1.0", tk.END).strip()
        if not description:
            messagebox.showwarning("Warning", "Please enter a description")
            return
        
        suggestions = action_suggester.suggest_actions(description)
        # Display suggestions in a dialog or panel
        self._display_suggestions(suggestions)
    
    def _display_suggestions(self, suggestions):
        """Display AI suggestions to the user."""
        if not suggestions:
            messagebox.showinfo("No Suggestions", "No suggestions found for your description")
            return
        
        # Create a simple suggestions display
        suggestion_text = "AI Suggestions:\n\n"
        for i, suggestion in enumerate(suggestions[:3], 1):
            suggestion_text += f"{i}. {suggestion.title}\n"
            suggestion_text += f"   {suggestion.description}\n"
            suggestion_text += f"   Confidence: {suggestion.confidence:.1%}\n\n"
        
        messagebox.showinfo("AI Suggestions", suggestion_text)
    
    def _update_ui(self):
        """Update the UI with current compound action data."""
        if not self.compound_action:
            return
        
        # Update basic info
        self.name_entry.delete(0, tk.END)
        if self.compound_action.name:
            self.name_entry.insert(0, self.compound_action.name)
        
        self.description_text.delete("1.0", tk.END)
        if self.compound_action.description:
            self.description_text.insert("1.0", self.compound_action.description)
        
        # Update overview
        self._update_overview()
        
        # Refresh YAML preview
        self._refresh_yaml_preview()
    
    def _update_overview(self):
        """Update the overview panel."""
        self.overview_text.config(state=tk.NORMAL)
        self.overview_text.delete("1.0", tk.END)
        
        if self.compound_action:
            overview = f"Name: {self.compound_action.name or 'Unnamed'}\n"
            overview += f"Description: {self.compound_action.description or 'No description'}\n"
            overview += f"Input Args: {len(self.compound_action.input_args or {})}\n"
            
            if self.compound_action.single_step:
                overview += "Steps: 1 (single step)\n"
            elif self.compound_action.steps:
                overview += f"Steps: {len(self.compound_action.steps)}\n"
            else:
                overview += "Steps: 0\n"
            
            self.overview_text.insert("1.0", overview)
        
        self.overview_text.config(state=tk.DISABLED)
    
    def _refresh_yaml_preview(self):
        """Refresh the YAML preview."""
        self.yaml_text.delete("1.0", tk.END)
        
        if self.compound_action:
            try:
                yaml_content = serialize_compound_action(self.compound_action)
                self.yaml_text.insert("1.0", yaml_content)
            except Exception as e:
                self.yaml_text.insert("1.0", f"Error generating YAML: {str(e)}")
    
    def _copy_yaml_to_clipboard(self):
        """Copy YAML content to clipboard."""
        yaml_content = self.yaml_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(yaml_content)
        self._set_status("YAML copied to clipboard")
    
    def _set_status(self, message: str):
        """Set the status bar message."""
        self.status_bar.config(text=message)
    
    # Placeholder methods for step and argument management
    def _add_input_argument(self):
        """Add a new input argument."""
        messagebox.showinfo("Add Argument", "Add argument dialog would open here")
    
    def _edit_input_argument(self):
        """Edit selected input argument."""
        messagebox.showinfo("Edit Argument", "Edit argument dialog would open here")
    
    def _remove_input_argument(self):
        """Remove selected input argument."""
        messagebox.showinfo("Remove Argument", "Remove argument confirmation would appear here")
    
    def _add_step(self):
        """Add a new step."""
        messagebox.showinfo("Add Step", "Add step dialog would open here")
    
    def _edit_step(self):
        """Edit selected step."""
        messagebox.showinfo("Edit Step", "Edit step dialog would open here")
    
    def _remove_step(self):
        """Remove selected step."""
        messagebox.showinfo("Remove Step", "Remove step confirmation would appear here")
    
    def _move_step_up(self):
        """Move selected step up."""
        messagebox.showinfo("Move Step", "Step would be moved up")
    
    def _move_step_down(self):
        """Move selected step down."""
        messagebox.showinfo("Move Step", "Step would be moved down")
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    app = MoveworksWizardGUI()
    app.run()


if __name__ == "__main__":
    main()
