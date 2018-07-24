# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.base.res.res_request import referenceable_models
from odoo.exceptions import ValidationError

class Tag(models.Model):
    _name = 'todo.task.tag'
    _description = 'To-do Tag'
    _parent_store = True
    
    # _parent_name = 'parent_id'
    name = fields.Char('Name')

    # Tag class relationship to Task:
    task_ids = fields.Many2many(
        'todo.task', #related model
        string='Tasks')

    parent_id = fields.Many2one(
        'todo.task.tag', 'Parent Tag', ondelete='restrict')
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)

    child_ids = fields.One2many(
        'todo.task.tag', 'parent_id', 'Child Tags')

class Stage(models.Model):
    _name = 'todo.task.stage'
    _description = 'To-do Stage'
    _order = 'sequence,name'

    # Stage class relationship with Tasks:
    tasks = fields.One2many(
            'todo.task', # related model
            'stage_id', # field for "this" on related model
            'Tasks in this stage')

    #String fields:
    name = fields.Char('Name', size=40, translate=True)
    desc = fields.Text('Description')

    state = fields.Selection(
        [('draft','New'), ('open','Started'), 
        ('done','Close')], 'State')
    docs = fields.Html('Documentation')

    # Numeric Fields:
    sequence = fields.Integer('Sequence')
    perc_complete = fields.Float('% Complete', (3, 2))

    # Date fields:
    date_effective = fields.Date('Effective Date')
    date_changed = fields.Datetime('Last Changed')

    #other fields:
    fold = fields.Boolean('Folded?')
    image = fields.Binary('Image')



class TodoTask(models.Model):
    _inherit = 'todo.task'

    # field _sql_constraints for check field name and field active must unique!!! 
    _sql_constraints = [('todo_task_name_uniq',
                        'UNIQUE (name, active)',
                        'Task title must be unique!')]

    # Old version code
    # refers_to = fields.Reference([('res.user','User'), ('res.partner', 'Partner')],
    #                             'Refers to') 

    # new version code
    refers_to = fields.Reference(referenceable_models, 'Refers to')

    stage_id = fields.Many2one('todo.task.stage', 'Stage')
    
    ####################################################
    # Task <-> Tag relation (positional args):
    # tag_ids = fields.Many2many(
    #     'todo.task.tag',        #related model
    #     'todo_task_tag_rel',    #relation table name
    #     'task_id',              #field for "this" record
    #     'tag_id',               #field for "other" record
    #     string='Tags')

    # Task <-> Tag relation (keyword args):
    tag_ids = fields.Many2many(
        comodel_name='todo.task.tag',        #related model
        relation='todo_task_tag_rel',    #relation table name
        column1='task_id',              #field for "this" record
        column2='tag_id',               #field for "other" record
        string='Tags')

    ####################################################

    stage_fold = fields.Boolean(
        'Stage Folded?',compute='_compute_stage_fold',
                        # store=False, # the default
                        search='_search_stage_fold',
                        inverse='_write_stage_fold')

    #below field ( stage_state ) using same stage with model=todo.task.stage ( field state ), so no need to code repeat
    stage_state = fields.Selection(
        related='stage_id.state', 
        string='Stage State')

    user_todo_count = fields.Integer(
        'User To-Do Count',
        compute='compute_user_todo_count')

    effort_estimate = fields.Integer('Effort Estimate')    

    #below function for checking or validation, field name must input text up to 5 charachter
    @api.constrains('name')
    def _check_name_size(self):
        for todo in self:
            if len(todo.name) < 5:
                raise ValidationError('Must have 5 chars!')

    @api.depends('stage_id.fold')
    def _compute_stage_fold(self):
        for task in self:
            task.stage_fold = task.stage_id.fold

    def _search_stage_fold(self, operator, value):
        return [('stage_id.fold', operator, value)]

    def _write_stage_fold(self, operator, value):
        self.stage_id.fold = self.stage_fold

    def compute_user_todo_count(self):
        for task in self:
            task.user_todo_count = task.search_count(
                [('user_id', '=', task.user_id.id)])

    

