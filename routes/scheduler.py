from flask import Flask, request, jsonify
from scheduler.scheduler_service import add_job, remove_job, get_jobs
from . import scheduler_bp
from flask import render_template

@scheduler_bp.route('/jobs', methods=['POST'])
def create_job():
    data = request.json
    job_id = data['job_id']
    func = data['func']
    trigger = data['trigger']
    trigger_args = data['trigger_args']
    add_job(job_id, func, trigger, **trigger_args)
    return jsonify({"message": "Job added successfully"}), 201

@scheduler_bp.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    remove_job(job_id)
    return jsonify({"message": "Job removed successfully"}), 200

@scheduler_bp.route('/jobs', methods=['GET'])
def list_jobs():
    jobs = get_jobs()
    job_list = [{"id": job.id, "next_run_time": str(job.next_run_time)} for job in jobs]
    return jsonify(job_list), 200

@scheduler_bp.route('/scheduler', methods=['GET'])
def scheduler():
    return render_template('scheduler.html')