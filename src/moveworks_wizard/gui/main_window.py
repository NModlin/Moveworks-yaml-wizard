"""
Main GUI window for the Moveworks Compound Action Wizard.

This module provides a tkinter-based graphical interface for creating
Compound Actions with enhanced user experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional, Dict, Any, List
import json
from pathlib import Path

from ..models.base import CompoundAction
from ..models.actions import ActionStep, ScriptStep
from ..models.control_flow import SwitchStep, SwitchCase
from ..models.terminal import ReturnStep, RaiseStep
from ..models.common import ProgressUpdates, DelayConfig
from ..serializers import serialize_compound_action
from ..templates.template_library import template_library
from ..ai.action_suggester import action_suggester
from ..bender.bender_assistant import bender_assistant
from ..catalog.builtin_actions import builtin_catalog
from ..utils.json_analyzer import JSONAnalyzer, VariableSuggestion


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
        ttk.Button(quick_start_frame, text="Analyze JSON",
                  command=self._show_json_analyzer).pack(fill=tk.X, pady=2)
        
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
        ttk.Button(args_buttons_frame, text="JSON Analysis",
                  command=self._analyze_json_for_args).pack(side=tk.LEFT, padx=2)
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
        description = self.ai_description.get("1.0", tk.END).strip()
        if not description:
            messagebox.showwarning("Warning", "Please enter a description in the AI Assistant section")
            return

        try:
            suggestions = action_suggester.suggest_actions(description)
            if suggestions:
                dialog = AISuggestionsDialog(self.root, suggestions, description)
                if dialog.result:
                    # Apply the selected suggestion
                    suggestion = dialog.result
                    self._apply_ai_suggestion(suggestion)
            else:
                messagebox.showinfo("No Suggestions", "No AI suggestions found for your description")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get AI suggestions: {str(e)}")

    def _show_bender_assistant(self):
        """Show the Bender assistant dialog."""
        dialog = BenderAssistantDialog(self.root)
        if dialog.result:
            # The result could be used to help with expressions
            pass

    def _show_template_library(self):
        """Show the template library dialog."""
        dialog = TemplateLibraryDialog(self.root)
        if dialog.result:
            template = dialog.result
            # Apply the template
            self.compound_action = template
            self._update_ui()
            self._set_status(f"Loaded template: {template.name}")
    
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

    def _apply_ai_suggestion(self, suggestion):
        """Apply an AI suggestion to create a compound action."""
        try:
            # Create a new compound action based on the suggestion
            self.compound_action = CompoundAction(
                name=suggestion.title,
                description=suggestion.description,
                input_args={},
                steps=[]
            )

            # Update the UI
            self._update_ui()
            self._set_status(f"Applied AI suggestion: {suggestion.title}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply suggestion: {str(e)}")
    
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
        
        # Update input arguments tree
        self._update_input_args_tree()

        # Update steps tree
        self._update_steps_tree()

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
    
    # Input argument management methods
    def _add_input_argument(self):
        """Add a new input argument."""
        dialog = InputArgumentDialog(self.root, "Add Input Argument")
        if dialog.result:
            name, value = dialog.result
            if self.compound_action:
                if not self.compound_action.input_args:
                    self.compound_action.input_args = {}
                self.compound_action.input_args[name] = value
                self._update_input_args_tree()
                self._update_overview()
                self._refresh_yaml_preview()
                self._set_status(f"Added input argument: {name}")

    def _edit_input_argument(self):
        """Edit selected input argument."""
        selection = self.input_args_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an argument to edit")
            return

        item = selection[0]
        name = self.input_args_tree.item(item, 'text')
        current_value = self.input_args_tree.item(item, 'values')[0]

        dialog = InputArgumentDialog(self.root, "Edit Input Argument", name, current_value)
        if dialog.result:
            new_name, new_value = dialog.result
            if self.compound_action and self.compound_action.input_args:
                # Remove old entry if name changed
                if new_name != name:
                    del self.compound_action.input_args[name]
                self.compound_action.input_args[new_name] = new_value
                self._update_input_args_tree()
                self._update_overview()
                self._refresh_yaml_preview()
                self._set_status(f"Updated input argument: {new_name}")

    def _remove_input_argument(self):
        """Remove selected input argument."""
        selection = self.input_args_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an argument to remove")
            return

        item = selection[0]
        name = self.input_args_tree.item(item, 'text')

        if messagebox.askyesno("Confirm", f"Remove input argument '{name}'?"):
            if self.compound_action and self.compound_action.input_args:
                del self.compound_action.input_args[name]
                self._update_input_args_tree()
                self._update_overview()
                self._refresh_yaml_preview()
                self._set_status(f"Removed input argument: {name}")
    
    def _add_step(self):
        """Add a new step."""
        if not self.compound_action:
            messagebox.showwarning("Warning", "Please create a compound action first")
            return

        dialog = StepDialog(self.root, "Add Step")
        if dialog.result:
            step = dialog.result
            if not self.compound_action.steps:
                self.compound_action.steps = []
            self.compound_action.steps.append(step)
            self._update_steps_tree()
            self._update_overview()
            self._refresh_yaml_preview()
            self._set_status("Added new step")

    def _edit_step(self):
        """Edit selected step."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step to edit")
            return

        item = selection[0]
        step_index = int(self.steps_tree.item(item, 'text')) - 1

        if self.compound_action and self.compound_action.steps:
            current_step = self.compound_action.steps[step_index]
            dialog = StepDialog(self.root, "Edit Step", current_step)
            if dialog.result:
                self.compound_action.steps[step_index] = dialog.result
                self._update_steps_tree()
                self._update_overview()
                self._refresh_yaml_preview()
                self._set_status("Updated step")

    def _remove_step(self):
        """Remove selected step."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step to remove")
            return

        item = selection[0]
        step_index = int(self.steps_tree.item(item, 'text')) - 1

        if messagebox.askyesno("Confirm", "Remove selected step?"):
            if self.compound_action and self.compound_action.steps:
                del self.compound_action.steps[step_index]
                self._update_steps_tree()
                self._update_overview()
                self._refresh_yaml_preview()
                self._set_status("Removed step")

    def _move_step_up(self):
        """Move selected step up."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step to move")
            return

        item = selection[0]
        step_index = int(self.steps_tree.item(item, 'text')) - 1

        if step_index > 0 and self.compound_action and self.compound_action.steps:
            # Swap with previous step
            steps = self.compound_action.steps
            steps[step_index], steps[step_index - 1] = steps[step_index - 1], steps[step_index]
            self._update_steps_tree()
            self._refresh_yaml_preview()
            self._set_status("Moved step up")

    def _move_step_down(self):
        """Move selected step down."""
        selection = self.steps_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a step to move")
            return

        item = selection[0]
        step_index = int(self.steps_tree.item(item, 'text')) - 1

        if (self.compound_action and self.compound_action.steps and
            step_index < len(self.compound_action.steps) - 1):
            # Swap with next step
            steps = self.compound_action.steps
            steps[step_index], steps[step_index + 1] = steps[step_index + 1], steps[step_index]
            self._update_steps_tree()
            self._refresh_yaml_preview()
            self._set_status("Moved step down")

    def _update_input_args_tree(self):
        """Update the input arguments tree view."""
        # Clear existing items
        for item in self.input_args_tree.get_children():
            self.input_args_tree.delete(item)

        # Add current input arguments
        if self.compound_action and self.compound_action.input_args:
            for name, value in self.compound_action.input_args.items():
                self.input_args_tree.insert('', 'end', text=name, values=(value,))

    def _update_steps_tree(self):
        """Update the steps tree view."""
        # Clear existing items
        for item in self.steps_tree.get_children():
            self.steps_tree.delete(item)

        # Add current steps
        if self.compound_action:
            if self.compound_action.single_step:
                step = self.compound_action.single_step
                step_type = step.__class__.__name__.replace('Step', '')
                details = self._get_step_details(step)
                self.steps_tree.insert('', 'end', text="1", values=(step_type, details))
            elif self.compound_action.steps:
                for i, step in enumerate(self.compound_action.steps, 1):
                    step_type = step.__class__.__name__.replace('Step', '')
                    details = self._get_step_details(step)
                    self.steps_tree.insert('', 'end', text=str(i), values=(step_type, details))

    def _get_step_details(self, step):
        """Get a summary of step details for display."""
        if hasattr(step, 'action_name'):
            return f"{step.action_name} → {step.output_key}"
        elif hasattr(step, 'code'):
            code_preview = step.code[:50] + "..." if len(step.code) > 50 else step.code
            return f"Script → {step.output_key}: {code_preview}"
        elif hasattr(step, 'cases'):
            return f"Switch with {len(step.cases)} cases"
        elif hasattr(step, 'value'):
            return f"Return: {step.value}"
        elif hasattr(step, 'error_code'):
            return f"Raise: {step.error_code}"
        else:
            return "Unknown step type"

    def _show_json_analyzer(self):
        """Show the JSON analyzer dialog."""
        dialog = JSONAnalyzerDialog(self.root)
        if dialog.result:
            suggestions = dialog.result
            # Show suggestions dialog
            suggestions_dialog = JSONSuggestionsDialog(self.root, suggestions)
            if suggestions_dialog.result:
                # Add selected suggestions as input arguments
                selected_suggestions = suggestions_dialog.result
                if self.compound_action:
                    if not self.compound_action.input_args:
                        self.compound_action.input_args = {}

                    for suggestion in selected_suggestions:
                        # Generate a better argument name
                        path_parts = suggestion.path.split('.')
                        if len(path_parts) > 1:
                            # Use last two parts for better context (e.g., "user_email" instead of just "email")
                            arg_name = '_'.join(path_parts[-2:]).lower()
                        else:
                            arg_name = path_parts[-1].lower()

                        # Ensure unique names
                        original_name = arg_name
                        counter = 1
                        while arg_name in self.compound_action.input_args:
                            arg_name = f"{original_name}_{counter}"
                            counter += 1

                        self.compound_action.input_args[arg_name] = suggestion.bender_expression

                    self._update_input_args_tree()
                    self._update_overview()
                    self._refresh_yaml_preview()

                    # Show success message
                    count = len(selected_suggestions)
                    messagebox.showinfo("Success",
                                      f"Added {count} variable{'s' if count != 1 else ''} as input arguments!\n\n"
                                      f"Check the 'Input Arguments' section to see them.")
                    self._set_status(f"Added {len(selected_suggestions)} arguments from JSON analysis")

    def _analyze_json_for_args(self):
        """Analyze JSON specifically for input arguments."""
        self._show_json_analyzer()

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


class InputArgumentDialog:
    """Dialog for adding/editing input arguments."""

    def __init__(self, parent, title, name="", value=""):
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Create form
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Name field
        ttk.Label(frame, text="Argument Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        self.name_entry.insert(0, name)

        # Value field
        ttk.Label(frame, text="Value (Bender expression):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.value_entry = ttk.Entry(frame, width=40)
        self.value_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        self.value_entry.insert(0, value)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        frame.columnconfigure(1, weight=1)

        # Focus on name entry
        self.name_entry.focus()

        # Wait for dialog to close
        self.dialog.wait_window()

    def _ok_clicked(self):
        name = self.name_entry.get().strip()
        value = self.value_entry.get().strip()

        if not name:
            messagebox.showwarning("Warning", "Please enter an argument name")
            return

        if not value:
            messagebox.showwarning("Warning", "Please enter a value")
            return

        self.result = (name, value)
        self.dialog.destroy()

    def _cancel_clicked(self):
        self.dialog.destroy()


class JSONAnalyzerDialog:
    """Dialog for JSON analysis input."""

    def __init__(self, parent):
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("JSON Analysis for Variable Suggestions")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = ttk.Label(main_frame,
                               text="Paste JSON from your HTTP connector test results to get variable suggestions:",
                               wraplength=550)
        instructions.pack(anchor=tk.W, pady=(0, 10))

        # Source name
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(source_frame, text="Data Source Name:").pack(side=tk.LEFT)
        self.source_entry = ttk.Entry(source_frame, width=30)
        self.source_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.source_entry.insert(0, "http_response")

        # JSON input area
        ttk.Label(main_frame, text="JSON Data:").pack(anchor=tk.W)
        self.json_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.json_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Load from File", command=self._load_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Analyze", command=self._analyze_json).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.RIGHT)

        # Focus on JSON text area
        self.json_text.focus()

        # Wait for dialog to close
        self.dialog.wait_window()

    def _load_file(self):
        """Load JSON from file."""
        filename = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    json_content = f.read()
                self.json_text.delete("1.0", tk.END)
                self.json_text.insert("1.0", json_content)

                # Set source name based on filename
                source_name = Path(filename).stem
                self.source_entry.delete(0, tk.END)
                self.source_entry.insert(0, source_name)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def _analyze_json(self):
        """Analyze the JSON and return suggestions."""
        json_data = self.json_text.get("1.0", tk.END).strip()
        source_name = self.source_entry.get().strip()

        if not json_data:
            messagebox.showwarning("Warning", "Please enter JSON data")
            return

        if not source_name:
            messagebox.showwarning("Warning", "Please enter a data source name")
            return

        try:
            analyzer = JSONAnalyzer()
            suggestions = analyzer.analyze_json(json_data, source_name)

            if not suggestions:
                messagebox.showinfo("No Suggestions", "No variable suggestions found in the JSON data")
                return

            self.result = suggestions
            self.dialog.destroy()

        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON data: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze JSON: {str(e)}")

    def _cancel_clicked(self):
        self.dialog.destroy()


class JSONSuggestionsDialog:
    """Dialog for selecting JSON analysis suggestions."""

    def __init__(self, parent, suggestions):
        self.result = None
        self.suggestions = suggestions

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Variable Suggestions")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = ttk.Label(main_frame,
                               text=f"Found {len(suggestions)} variable suggestions. Click to select variables, then click 'Add Selected':",
                               wraplength=750)
        instructions.pack(anchor=tk.W, pady=(0, 5))

        # Selection help
        help_text = ttk.Label(main_frame,
                            text="💡 Tip: Hold Ctrl to select multiple items, or use the Quick Selection buttons",
                            wraplength=750,
                            foreground="blue")
        help_text.pack(anchor=tk.W, pady=(0, 10))

        # Quick Selection buttons - moved to top
        selection_frame = ttk.LabelFrame(main_frame, text="Quick Selection", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(selection_frame, text="Select All", command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(selection_frame, text="Select None", command=self._select_none).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(selection_frame, text="Select Top 5", command=self._select_top_5).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(selection_frame, text="Select Common", command=self._select_common).pack(side=tk.LEFT)

        # Action buttons - pack at bottom FIRST to reserve space
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Add a label to show selection count
        self.selection_label = ttk.Label(button_frame, text="No items selected")
        self.selection_label.pack(side=tk.LEFT)

        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.RIGHT)
        self.add_button = ttk.Button(button_frame, text="Add Selected (0)", command=self._add_selected)
        self.add_button.pack(side=tk.RIGHT, padx=(5, 5))

        # Create treeview for suggestions with multiple selection
        columns = ('Type', 'Description', 'Bender Expression')
        self.suggestions_tree = ttk.Treeview(main_frame, columns=columns, height=15, selectmode='extended')

        # Configure columns
        self.suggestions_tree.heading('#0', text='Variable Path')
        self.suggestions_tree.heading('Type', text='Type')
        self.suggestions_tree.heading('Description', text='Description')
        self.suggestions_tree.heading('Bender Expression', text='Bender Expression')

        self.suggestions_tree.column('#0', width=200)
        self.suggestions_tree.column('Type', width=100)
        self.suggestions_tree.column('Description', width=200)
        self.suggestions_tree.column('Bender Expression', width=250)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.suggestions_tree.yview)
        self.suggestions_tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar - after buttons are packed
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.suggestions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate suggestions
        for suggestion in suggestions:
            self.suggestions_tree.insert('', 'end',
                                       text=suggestion.path,
                                       values=(suggestion.data_type,
                                             suggestion.description,
                                             suggestion.bender_expression))

        # Bind selection change event
        self.suggestions_tree.bind('<<TreeviewSelect>>', self._on_selection_change)

        # Bind keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self._add_selected())
        self.dialog.bind('<Escape>', lambda e: self._cancel_clicked())

        # Focus on the tree for keyboard navigation
        self.suggestions_tree.focus_set()

        # Wait for dialog to close
        self.dialog.wait_window()

    def _select_all(self):
        """Select all suggestions."""
        for item in self.suggestions_tree.get_children():
            self.suggestions_tree.selection_add(item)

    def _select_none(self):
        """Deselect all suggestions."""
        self.suggestions_tree.selection_remove(self.suggestions_tree.selection())

    def _select_top_5(self):
        """Select the top 5 suggestions."""
        self._select_none()

        # Select first 5 items (they're already prioritized)
        children = self.suggestions_tree.get_children()
        for item in children[:5]:
            self.suggestions_tree.selection_add(item)

    def _select_common(self):
        """Select common/useful suggestions."""
        self._select_none()

        # Select suggestions with common patterns
        common_patterns = ['id', 'email', 'name', 'status', 'user', 'data']

        for item in self.suggestions_tree.get_children():
            path = self.suggestions_tree.item(item, 'text').lower()
            if any(pattern in path for pattern in common_patterns):
                self.suggestions_tree.selection_add(item)

    def _on_selection_change(self, event):
        """Handle selection change in the treeview."""
        selection = self.suggestions_tree.selection()
        count = len(selection)

        # Update button text and label
        self.add_button.config(text=f"Add Selected ({count})")

        if count == 0:
            self.selection_label.config(text="No items selected")
        elif count == 1:
            self.selection_label.config(text="1 item selected")
        else:
            self.selection_label.config(text=f"{count} items selected")

    def _add_selected(self):
        """Add selected suggestions."""
        selection = self.suggestions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select at least one suggestion")
            return

        selected_suggestions = []
        for item in selection:
            path = self.suggestions_tree.item(item, 'text')
            # Find the corresponding suggestion object
            for suggestion in self.suggestions:
                if suggestion.path == path:
                    selected_suggestions.append(suggestion)
                    break

        # Show confirmation with details
        count = len(selected_suggestions)
        if count > 5:
            # For many selections, show summary
            message = f"Add {count} variables as input arguments?\n\nFirst 5:\n"
            for i, suggestion in enumerate(selected_suggestions[:5]):
                path_parts = suggestion.path.split('.')
                if len(path_parts) > 1:
                    arg_name = '_'.join(path_parts[-2:]).lower()
                else:
                    arg_name = path_parts[-1].lower()
                message += f"• {arg_name}\n"
            if count > 5:
                message += f"... and {count - 5} more"
        else:
            # For few selections, show all
            message = f"Add these {count} variables as input arguments?\n\n"
            for suggestion in selected_suggestions:
                path_parts = suggestion.path.split('.')
                if len(path_parts) > 1:
                    arg_name = '_'.join(path_parts[-2:]).lower()
                else:
                    arg_name = path_parts[-1].lower()
                message += f"• {arg_name} ← {suggestion.path}\n"

        if messagebox.askyesno("Confirm Selection", message):
            self.result = selected_suggestions
            self.dialog.destroy()

    def _cancel_clicked(self):
        self.dialog.destroy()


class StepDialog:
    """Dialog for adding/editing steps."""

    def __init__(self, parent, title, step=None):
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Step type selection
        ttk.Label(main_frame, text="Step Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.step_type = ttk.Combobox(main_frame, values=["Action", "Script", "Return"], state="readonly")
        self.step_type.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        self.step_type.set("Action")
        self.step_type.bind("<<ComboboxSelected>>", self._on_step_type_changed)

        # Output key with auto-fill button
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        output_frame.columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="Output Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_key_entry = ttk.Entry(output_frame, width=30)
        self.output_key_entry.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 5))
        ttk.Button(output_frame, text="Auto", width=6,
                  command=self._auto_fill_output_key).grid(row=0, column=1)

        # Action name with suggestions
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        action_frame.columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="Action Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.action_name_entry = ttk.Combobox(action_frame, width=30)
        self.action_name_entry.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 5))
        self.action_name_entry.bind("<KeyRelease>", self._on_action_name_changed)
        ttk.Button(action_frame, text="Suggest", width=6,
                  command=self._suggest_action_names).grid(row=0, column=1)

        # Code (for script steps) with templates
        code_frame = ttk.Frame(main_frame)
        code_frame.grid(row=3, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        code_frame.columnconfigure(0, weight=1)
        code_frame.rowconfigure(0, weight=1)

        ttk.Label(main_frame, text="Code:").grid(row=3, column=0, sticky=tk.W+tk.N, pady=5)
        self.code_text = scrolledtext.ScrolledText(code_frame, height=6, width=40)
        self.code_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=(0, 5))

        code_buttons_frame = ttk.Frame(code_frame)
        code_buttons_frame.grid(row=0, column=1, sticky=tk.N)
        ttk.Button(code_buttons_frame, text="Template", width=8,
                  command=self._insert_code_template).pack(pady=2)
        ttk.Button(code_buttons_frame, text="Clear", width=8,
                  command=self._clear_code).pack(pady=2)

        # Value (for return steps) with suggestions
        value_frame = ttk.Frame(main_frame)
        value_frame.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        value_frame.columnconfigure(0, weight=1)

        ttk.Label(main_frame, text="Return Value:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.value_entry = ttk.Combobox(value_frame, width=30)
        self.value_entry.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 5))
        ttk.Button(value_frame, text="Suggest", width=6,
                  command=self._suggest_return_values).grid(row=0, column=1)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="OK", command=self._ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel_clicked).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Populate if editing existing step
        if step:
            self._populate_from_step(step)

        # Focus on output key
        self.output_key_entry.focus()

        # Wait for dialog to close
        self.dialog.wait_window()

    def _populate_from_step(self, step):
        """Populate dialog fields from existing step."""
        if hasattr(step, 'output_key'):
            self.output_key_entry.insert(0, step.output_key)

        if hasattr(step, 'action_name'):
            self.step_type.set("Action")
            self.action_name_entry.insert(0, step.action_name)
        elif hasattr(step, 'code'):
            self.step_type.set("Script")
            self.code_text.insert("1.0", step.code)
        elif hasattr(step, 'value'):
            self.step_type.set("Return")
            self.value_entry.insert(0, str(step.value))

    def _ok_clicked(self):
        step_type = self.step_type.get()
        output_key = self.output_key_entry.get().strip()

        if not output_key:
            messagebox.showwarning("Warning", "Please enter an output key")
            return

        try:
            if step_type == "Action":
                action_name = self.action_name_entry.get().strip()
                if not action_name:
                    messagebox.showwarning("Warning", "Please enter an action name")
                    return

                from ..models.actions import ActionStep
                step = ActionStep(
                    action_name=action_name,
                    output_key=output_key
                )

            elif step_type == "Script":
                code = self.code_text.get("1.0", tk.END).strip()
                if not code:
                    messagebox.showwarning("Warning", "Please enter script code")
                    return

                from ..models.actions import ScriptStep
                step = ScriptStep(
                    code=code,
                    output_key=output_key
                )

            elif step_type == "Return":
                value = self.value_entry.get().strip()
                if not value:
                    messagebox.showwarning("Warning", "Please enter a return value")
                    return

                from ..models.terminal import ReturnStep
                step = ReturnStep(value=value)

            else:
                messagebox.showerror("Error", "Invalid step type")
                return

            self.result = step
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create step: {str(e)}")

    def _cancel_clicked(self):
        self.dialog.destroy()

    def _on_step_type_changed(self, event=None):
        """Handle step type change to auto-fill output key."""
        self._auto_fill_output_key()

    def _auto_fill_output_key(self):
        """Auto-generate output key based on step type and action name."""
        step_type = self.step_type.get()

        if step_type == "Action":
            action_name = self.action_name_entry.get().strip()
            if action_name:
                # Generate output key from action name
                # Remove 'mw.' prefix if present
                clean_name = action_name.replace('mw.', '')
                # Convert to snake_case and add suffix
                output_key = clean_name.lower().replace('.', '_').replace('-', '_') + "_result"
                self.output_key_entry.delete(0, tk.END)
                self.output_key_entry.insert(0, output_key)
            else:
                # Default for action steps
                self.output_key_entry.delete(0, tk.END)
                self.output_key_entry.insert(0, "action_result")
        elif step_type == "Script":
            self.output_key_entry.delete(0, tk.END)
            self.output_key_entry.insert(0, "script_result")
        elif step_type == "Return":
            self.output_key_entry.delete(0, tk.END)
            self.output_key_entry.insert(0, "final_result")

    def _on_action_name_changed(self, event=None):
        """Handle action name change to update suggestions and output key."""
        # Auto-update output key when action name changes
        self._auto_fill_output_key()

        # Update action name suggestions
        current_text = self.action_name_entry.get()
        if len(current_text) >= 2:  # Start suggesting after 2 characters
            suggestions = self._get_action_name_suggestions(current_text)
            self.action_name_entry['values'] = suggestions

    def _suggest_action_names(self):
        """Show action name suggestions."""
        try:
            from ..catalog.builtin_actions import builtin_catalog

            # Get all built-in actions
            builtin_actions = []
            for category, actions in builtin_catalog.get_all_actions().items():
                for action in actions:
                    builtin_actions.append(action.action_name)
        except ImportError:
            builtin_actions = []

        # Common custom action patterns
        common_patterns = [
            "fetch_user_details",
            "create_ticket",
            "send_notification",
            "update_database",
            "validate_input",
            "process_data",
            "generate_report",
            "check_permissions"
        ]

        all_suggestions = builtin_actions + common_patterns
        self.action_name_entry['values'] = all_suggestions
        self.action_name_entry.event_generate('<Button-1>')

    def _get_action_name_suggestions(self, partial_text):
        """Get action name suggestions based on partial text."""
        suggestions = []
        partial_lower = partial_text.lower()

        try:
            from ..catalog.builtin_actions import builtin_catalog
            # Get matching built-in actions
            for category, actions in builtin_catalog.get_all_actions().items():
                for action in actions:
                    if partial_lower in action.action_name.lower():
                        suggestions.append(action.action_name)
        except ImportError:
            pass

        # Add common patterns that match
        common_patterns = [
            "fetch_user_details", "create_ticket", "send_notification",
            "update_database", "validate_input", "process_data"
        ]

        for pattern in common_patterns:
            if partial_lower in pattern.lower():
                suggestions.append(pattern)

        return suggestions[:10]  # Limit to 10 suggestions

    def _insert_code_template(self):
        """Insert a code template into the script area."""
        templates = {
            "Basic Processing": "# Process the input data\nresult = data.input_field\nreturn result",
            "Data Validation": "# Validate input data\nif not data.required_field:\n    raise ValueError('Required field is missing')\nreturn {'valid': True}",
            "List Processing": "# Process a list of items\nresults = []\nfor item in data.items:\n    processed = item.upper()  # Example processing\n    results.append(processed)\nreturn results",
            "API Response": "# Process API response\nif response.status_code == 200:\n    return response.data\nelse:\n    raise Exception(f'API error: {response.status_code}')",
            "String Manipulation": "# String processing example\ntext = data.input_text\nprocessed = text.strip().lower().replace(' ', '_')\nreturn {'processed_text': processed}"
        }

        # Create a simple selection dialog
        template_dialog = tk.Toplevel(self.dialog)
        template_dialog.title("Select Code Template")
        template_dialog.geometry("400x300")
        template_dialog.transient(self.dialog)
        template_dialog.grab_set()

        # Template list
        listbox = tk.Listbox(template_dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for template_name in templates.keys():
            listbox.insert(tk.END, template_name)

        def insert_selected():
            selection = listbox.curselection()
            if selection:
                template_name = listbox.get(selection[0])
                template_code = templates[template_name]
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert("1.0", template_code)
                template_dialog.destroy()

        # Buttons
        button_frame = ttk.Frame(template_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text="Insert", command=insert_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=template_dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _clear_code(self):
        """Clear the code text area."""
        self.code_text.delete("1.0", tk.END)

    def _suggest_return_values(self):
        """Suggest common return value patterns."""
        suggestions = [
            "data.processed_result",
            "{'status': 'success', 'data': data.result}",
            "data.output_field",
            "{'message': 'Operation completed'}",
            "data.final_value",
            "{'result': data.computed_value}",
            "data.response",
            "{'success': True, 'value': data.result}"
        ]

        self.value_entry['values'] = suggestions
        self.value_entry.event_generate('<Button-1>')


def main():
    """Main entry point for the GUI application."""
    app = MoveworksWizardGUI()
    app.run()


if __name__ == "__main__":
    main()
