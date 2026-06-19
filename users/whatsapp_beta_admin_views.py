# ─── WhatsApp Beta Admin Management Views ────────────────────────────────

import json
import logging
from datetime import datetime, timedelta
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from users.whatsapp_beta_regulator import WhatsAppBetaRegulator
from users.whatsapp_beta_config import WhatsAppBetaConfig

logger = logging.getLogger(__name__)


def admin_whatsapp_beta_dashboard(request):
    """
    Admin dashboard for WhatsApp beta testing management
    """
    
    # Check if user is admin
    if not request.user.is_staff:
        return render(request, "users/error.html", {
            "error": "You don't have permission to access this page",
            "title": "Access Denied"
        })
    
    try:
        # Get overall statistics
        with connection.cursor() as cursor:
            # Total beta testers
            cursor.execute("SELECT COUNT(*) FROM whatsapp_beta_testers WHERE is_approved = 1")
            approved_count = cursor.fetchone()[0]
            
            # Pending approvals
            cursor.execute("SELECT COUNT(*) FROM whatsapp_beta_testers WHERE is_approved = 0")
            pending_count = cursor.fetchone()[0]
            
            # Active users
            cursor.execute("SELECT COUNT(*) FROM whatsapp_beta_testers WHERE is_active = 1 AND is_approved = 1")
            active_count = cursor.fetchone()[0]
            
            # Messages sent (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM whatsapp_beta_usage_logs
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                AND status = 'success'
            """)
            messages_24h = cursor.fetchone()[0]
            
            # Messages sent (last 7 days)
            cursor.execute("""
                SELECT COUNT(*) FROM whatsapp_beta_usage_logs
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                AND status = 'success'
            """)
            messages_7d = cursor.fetchone()[0]
            
            # Pending alerts
            cursor.execute("SELECT COUNT(*) FROM whatsapp_beta_compliance WHERE is_resolved = 0")
            pending_alerts = cursor.fetchone()[0]
            
            # Recent alerts
            cursor.execute("""
                SELECT id, user_id, alert_type, severity, message, timestamp
                FROM whatsapp_beta_compliance
                WHERE is_resolved = 0
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            
            columns = ['id', 'user_id', 'alert_type', 'severity', 'message', 'timestamp']
            recent_alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get pending approvals
            cursor.execute("""
                SELECT user_id, email, role, date_joined_beta
                FROM whatsapp_beta_testers
                WHERE is_approved = 0
                ORDER BY date_joined_beta DESC
                LIMIT 10
            """)
            
            columns = ['user_id', 'email', 'role', 'date_joined_beta']
            pending_approvals = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        context = {
            "beta_enabled": WhatsAppBetaConfig.BETA_ENABLED,
            "beta_version": WhatsAppBetaConfig.BETA_VERSION,
            
            # Statistics
            "approved_count": approved_count,
            "pending_count": pending_count,
            "active_count": active_count,
            "messages_24h": messages_24h,
            "messages_7d": messages_7d,
            "pending_alerts": pending_alerts,
            
            # Details
            "recent_alerts": recent_alerts,
            "pending_approvals": pending_approvals,
            
            # Features
            "features": WhatsAppBetaConfig.FEATURES,
            "rate_limits": WhatsAppBetaConfig.RATE_LIMITS,
        }
        
        return render(request, "users/whatsapp_beta_admin.html", context)
        
    except Exception as e:
        logger.error(f"Error loading WhatsApp beta dashboard: {e}")
        return render(request, "users/error.html", {
            "error": "Error loading dashboard",
            "title": "Error"
        })


@require_http_methods(["POST"])
def approve_beta_tester(request):
    """Approve a user for beta testing"""
    
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    
    try:
        user_id = request.POST.get("user_id")
        daily_limit = int(request.POST.get("daily_limit", 100))
        
        if not user_id:
            return JsonResponse({"success": False, "error": "User ID required"})
        
        success, message = WhatsAppBetaRegulator.approve_beta_tester(
            user_id, request.user.id, daily_limit
        )
        
        return JsonResponse({
            "success": success,
            "message": message
        })
        
    except Exception as e:
        logger.error(f"Error approving beta tester: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["POST"])
def deactivate_beta_tester(request):
    """Deactivate a user from beta testing"""
    
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    
    try:
        user_id = request.POST.get("user_id")
        reason = request.POST.get("reason", "")
        
        if not user_id:
            return JsonResponse({"success": False, "error": "User ID required"})
        
        success, message = WhatsAppBetaRegulator.deactivate_beta_tester(user_id, reason)
        
        return JsonResponse({
            "success": success,
            "message": message
        })
        
    except Exception as e:
        logger.error(f"Error deactivating beta tester: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


def get_beta_tester_details(request):
    """Get detailed information about a beta tester"""
    
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    try:
        user_id = request.GET.get("user_id")
        
        if not user_id:
            return JsonResponse({"error": "User ID required"})
        
        with connection.cursor() as cursor:
            # Get tester info
            cursor.execute("""
                SELECT user_id, email, role, is_approved, is_active,
                       daily_message_limit, messages_sent_today,
                       total_messages_sent, last_used, date_joined_beta
                FROM whatsapp_beta_testers
                WHERE user_id = %s
            """, [user_id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({"error": "User not found"})
            
            tester_data = {
                "user_id": result[0],
                "email": result[1],
                "role": result[2],
                "is_approved": result[3],
                "is_active": result[4],
                "daily_limit": result[5],
                "messages_today": result[6],
                "total_messages": result[7],
                "last_used": result[8].isoformat() if result[8] else None,
                "date_joined": result[9].isoformat() if result[9] else None,
            }
            
            # Get usage stats (last 7 days)
            stats = WhatsAppBetaRegulator.get_usage_statistics(user_id, 7)
            
            # Get recent alerts
            cursor.execute("""
                SELECT alert_type, severity, message, timestamp, is_resolved
                FROM whatsapp_beta_compliance
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT 10
            """, [user_id])
            
            columns = ['alert_type', 'severity', 'message', 'timestamp', 'is_resolved']
            recent_alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return JsonResponse({
                "success": True,
                "tester": tester_data,
                "stats": stats,
                "recent_alerts": recent_alerts
            })
            
    except Exception as e:
        logger.error(f"Error getting tester details: {e}")
        return JsonResponse({
            "error": str(e)
        }, status=500)


def get_compliance_alerts(request):
    """Get compliance alerts with filtering"""
    
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    try:
        limit = int(request.GET.get("limit", 50))
        offset = int(request.GET.get("offset", 0))
        severity = request.GET.get("severity", "")
        is_resolved = request.GET.get("is_resolved", "")
        
        query = "SELECT id, user_id, alert_type, severity, message, timestamp, is_resolved FROM whatsapp_beta_compliance WHERE 1=1"
        params = []
        
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        
        if is_resolved != "":
            query += f" AND is_resolved = %s"
            params.append(is_resolved == "true")
        
        query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            
            columns = ['id', 'user_id', 'alert_type', 'severity', 'message', 'timestamp', 'is_resolved']
            alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM whatsapp_beta_compliance WHERE 1=1"
            count_params = []
            
            if severity:
                count_query += " AND severity = %s"
                count_params.append(severity)
            
            if is_resolved != "":
                count_query += f" AND is_resolved = %s"
                count_params.append(is_resolved == "true")
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()[0]
        
        return JsonResponse({
            "success": True,
            "alerts": alerts,
            "total": total,
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        logger.error(f"Error getting compliance alerts: {e}")
        return JsonResponse({
            "error": str(e)
        }, status=500)


@require_http_methods(["POST"])
def resolve_compliance_alert(request):
    """Resolve a compliance alert"""
    
    if not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    
    try:
        alert_id = request.POST.get("alert_id")
        resolution_notes = request.POST.get("resolution_notes", "")
        
        if not alert_id:
            return JsonResponse({"success": False, "error": "Alert ID required"})
        
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE whatsapp_beta_compliance
                SET is_resolved = 1,
                    resolved_by_id = %s,
                    resolved_at = NOW(),
                    resolution_notes = %s
                WHERE id = %s
            """, [request.user.id, resolution_notes, alert_id])
        
        logger.info(f"Compliance alert resolved: alert_id={alert_id}")
        
        return JsonResponse({
            "success": True,
            "message": "Alert resolved successfully"
        })
        
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
