import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from PIL import Image

from math_utils import *
from vector3 import *
from ui import *

def drawOrigin():
    glBegin(GL_LINES)
    glColor(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(1000,0,0)
    glColor(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0,1000,0)
    glColor(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0,0,1000)
    glEnd()

def loadTexture(texture_path):
    image = Image.open(texture_path)
    image = image.convert("RGBA")

    img_data = image.tobytes()
    width, height = image.size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id

def drawGridPlane(cam, bodies, vessels):
    if cam.pos.y != 0:
        spacing = 10**(int(math.log(abs(cam.pos.y), 10)) + 3)
        scene_spacing = spacing * visual_scaling_factor
        # size = abs(cam.pos.y) * 10

        N = 150
        corner_x = (-cam.pos.x - N * 0.5 * scene_spacing) + cam.pos.x % (scene_spacing)
        corner_z = (-cam.pos.z - N * 0.5 * scene_spacing) + cam.pos.z % (scene_spacing)

        glColor(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        for i in range(N + 1):
            cx = corner_x + i * scene_spacing
            z0 = corner_z
            z1 = corner_z + N * scene_spacing
            glVertex3f(cx, 0, z0)
            glVertex3f(cx, 0, z1)

        for i in range(N + 1):
            x0 = corner_x
            x1 = corner_x + N * scene_spacing
            cz = corner_z + i * scene_spacing
            glVertex3f(x0, 0, cz)
            glVertex3f(x1, 0, cz)
        glEnd()
    else:
        spacing = 0

    glBegin(GL_LINES)
    for b in bodies:
        glColor(b.get_color()[0] * 0.9, b.get_color()[1] * 0.9, b.get_color()[2] * 0.9)
        glVertex3f(b.get_draw_pos().x, 0, b.get_draw_pos().z)
        glVertex3f(b.get_draw_pos().x, b.get_draw_pos().y, b.get_draw_pos().z)

    for v in vessels:
        glColor(v.get_color()[0] * 0.9, v.get_color()[1] * 0.9, v.get_color()[2] * 0.9)
        glVertex3f(v.get_draw_pos().x, 0, v.get_draw_pos().z)
        glVertex3f(v.get_draw_pos().x, v.get_draw_pos().y, v.get_draw_pos().z)
    glEnd()

    return spacing

def drawPolarGridPlane(cam, bodies, vessels, angular_divisions=64):
    if cam.pos.y != 0:
        radial_spacing = 10**(int(math.log(abs(cam.pos.y), 10)) + 3)

        N = 1e6 # random value above 64
        while N > 64:
            scene_radial_spacing = radial_spacing * visual_scaling_factor

            cam_planar_dist = (cam.pos.x**2 + cam.pos.z**2)**0.5
            N = max(int(cam_planar_dist / scene_radial_spacing * 2) + 1, 24)

            if N > 64:
                radial_spacing *= 10
            
        dtheta = 2 * math.pi / angular_divisions

        glColor(0.3, 0.3, 0.3)
            
        for i in range(N + 1):
            ang_points = []
            glBegin(GL_LINES)
            for j in range(angular_divisions):
                theta = dtheta * j
                x = math.cos(theta)
                z = math.sin(theta)
                r = i * scene_radial_spacing

                if i == N:
                    glVertex3f(0, 0, 0)
                    glVertex3f(x * r, 0, z * r)
                ang_points.append([x * r, 0, z * r])

            glEnd()
            glBegin(GL_LINE_STRIP)
            # tangential lines
            for j in range(1, angular_divisions):
                glVertex3f(ang_points[j-1][0], 0, ang_points[j-1][2])
                glVertex3f(ang_points[j][0], 0, ang_points[j][2])

            glVertex3f(ang_points[-1][0], 0, ang_points[-1][2])
            glVertex3f(ang_points[0][0], 0, ang_points[0][2])

            glEnd()
    else:
        radial_spacing = 0

    glBegin(GL_LINES)
    for b in bodies:
        glColor(b.get_color()[0] * 0.9, b.get_color()[1] * 0.9, b.get_color()[2] * 0.9)
        glVertex3f(b.get_draw_pos().x, 0, b.get_draw_pos().z)
        glVertex3f(b.get_draw_pos().x, b.get_draw_pos().y, b.get_draw_pos().z)

    for v in vessels:
        glColor(v.get_color()[0] * 0.9, v.get_color()[1] * 0.9, v.get_color()[2] * 0.9)
        glVertex3f(v.get_draw_pos().x, 0, v.get_draw_pos().z)
        glVertex3f(v.get_draw_pos().x, v.get_draw_pos().y, v.get_draw_pos().z)
    glEnd()

    return radial_spacing

def drawBodies(bodies, active_cam, draw_mode, pmcs_visible):

    for b in bodies:

        if (draw_mode == 1 or draw_mode == 2) and b.surface_map_path != None:
            glColor(1, 1, 1)
        else:
            glColor(b.get_color()[0], b.get_color()[1], b.get_color()[2])

        b.update_draw_pos()

        # texture_path = "data/images/surface_maps/earth.png"
        # texture_id = loadTexture(texture_path)
        if b.surface_map_path:
            texture_id = b.surface_map
        
        glPushMatrix()
        glTranslatef(b.get_draw_pos().x, b.get_draw_pos().y, b.get_draw_pos().z)

        # if the object is too far and appears too small, we can just draw it as a point
        # (cam and object coord systems are opposite for some reason!!)
        camera_distance = (-b.get_draw_pos() - active_cam.get_pos()).mag()
        camera_physical_distance = camera_distance / visual_scaling_factor

        if math.degrees(math.atan(b.get_radius()*2/camera_physical_distance)) < 0.2: #0.85:
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()

        else:
            if draw_mode == 1 or draw_mode == 2:
                if b.surface_map_path:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, texture_id)
                    glPolygonMode(GL_FRONT, GL_FILL)
                    glBegin(GL_TRIANGLES)

                    for face in b.model.faces:
                        for i in range(3):
                            try:
                                u = b.model.texture_coords[face[1][i]-1][0]
                                v = b.model.texture_coords[face[1][i]-1][1]
                            except Exception as e:
                                print(e)
                                print(face)
                                print(i)
                                print(face[1][i])

                            vertex_x = b.model.vertices[face[0][i]-1][0]
                            vertex_y = b.model.vertices[face[0][i]-1][1]
                            vertex_z = b.model.vertices[face[0][i]-1][2]

                            vertex_i = numpy.matmul(numpy.array([vertex_x, vertex_y, vertex_z]), b.orient.tolist())

                            glTexCoord2f(u, v)
                            glVertex3f(vertex_i[0], vertex_i[1], vertex_i[2])

                    glEnd()
                    glBindTexture(GL_TEXTURE_2D, 0)
                    glDisable(GL_TEXTURE_2D)
                else:
                    glPolygonMode(GL_FRONT, GL_FILL)
                    glBegin(GL_TRIANGLES)
                    for face in b.model.faces:
                        for i in range(3):
                            vertex_x = b.model.vertices[face[0][i]-1][0]
                            vertex_y = b.model.vertices[face[0][i]-1][1]
                            vertex_z = b.model.vertices[face[0][i]-1][2]

                            vertex_i = numpy.matmul(numpy.array([vertex_x, vertex_y, vertex_z]), b.orient.tolist())

                            glVertex3f(vertex_i[0], vertex_i[1], vertex_i[2])
                    glEnd()

            if draw_mode == 0 or draw_mode == 2:
                glPolygonMode(GL_FRONT, GL_LINE)
                
                if draw_mode == 2:
                    # darken color a bit so that lines are actually visible
                    glColor(b.get_color()[0]/1.25, b.get_color()[1]/1.25, b.get_color()[2]/1.25)
                    
                glBegin(GL_TRIANGLES)
                for face in b.model.faces:
                    for i in range(3):
                        vertex_x = b.model.vertices[face[0][i]-1][0]
                        vertex_y = b.model.vertices[face[0][i]-1][1]
                        vertex_z = b.model.vertices[face[0][i]-1][2]

                        vertex_i = numpy.matmul(numpy.array([vertex_x, vertex_y, vertex_z]), b.orient.tolist())

                        glVertex3f(vertex_i[0], vertex_i[1], vertex_i[2])
                glEnd()

        glPopMatrix()

        # glDeleteTextures([texture_id])

        if pmcs_visible and b.point_mass_cloud:
            for idx_pm in range(len(b.point_mass_cloud)):
                abs_pos, pm_mass = b.get_pm_abs(idx_pm)
                draw_pos = abs_pos * visual_scaling_factor
                cam_dist = (-draw_pos - active_cam.get_pos()).mag()
                crossline_length = pm_mass / b.mass * 1500 # yes, 500 is arbitrary
                
                # glColor(b.get_color()) -- we already did this
                glPushMatrix()
                glTranslate(draw_pos.x, draw_pos.y, draw_pos.z)
                glBegin(GL_LINES)

                # this creates an octahedron
                #
                # ...
                # trust me
                glVertex3f(-crossline_length * 0.5, 0, 0)
                glVertex3f(crossline_length * 0.5, 0, 0)

                glVertex3f(0, -crossline_length * 0.5, 0)
                glVertex3f(0, crossline_length * 0.5, 0)

                glVertex3f(0, 0, -crossline_length * 0.5)
                glVertex3f(0, 0, crossline_length * 0.5)

                glVertex3f(0, 0, -crossline_length * 0.5)
                glVertex3f(0, crossline_length * 0.5, 0)

                glVertex3f(0, 0, crossline_length * 0.5)
                glVertex3f(0, crossline_length * 0.5, 0)

                glVertex3f(crossline_length * 0.5, 0, 0)
                glVertex3f(0, crossline_length * 0.5, 0)

                glVertex3f(-crossline_length * 0.5, 0, 0)
                glVertex3f(0, crossline_length * 0.5, 0)

                glVertex3f(0, 0, -crossline_length * 0.5)
                glVertex3f(0, -crossline_length * 0.5, 0)

                glVertex3f(0, 0, crossline_length * 0.5)
                glVertex3f(0, -crossline_length * 0.5, 0)

                glVertex3f(crossline_length * 0.5, 0, 0)
                glVertex3f(0, -crossline_length * 0.5, 0)

                glVertex3f(-crossline_length * 0.5, 0, 0)
                glVertex3f(0, -crossline_length * 0.5, 0)

                glVertex3f(-crossline_length * 0.5, 0, 0)
                glVertex3f(0, 0, crossline_length * 0.5)

                glVertex3f(crossline_length * 0.5, 0, 0)
                glVertex3f(0, 0, crossline_length * 0.5)

                glVertex3f(-crossline_length * 0.5, 0, 0)
                glVertex3f(0, 0, -crossline_length * 0.5)

                glVertex3f(crossline_length * 0.5, 0, 0)
                glVertex3f(0, 0, -crossline_length * 0.5)

                glEnd()
                glPopMatrix()

def drawVessels(vessels, active_cam, draw_mode):

    for v in vessels:
        # change color we render with
        glColor(v.get_color()[0], v.get_color()[1], v.get_color()[2])

        v.update_draw_pos()

        # here we go
        glPushMatrix()

        # put us in correct position
        glTranslatef(v.get_draw_pos().x, v.get_draw_pos().y, v.get_draw_pos().z)

        # if the vessel is too far away from camera, just draw a point and don't bother
        # with the whole object
        # (cam and object coord systems are opposite for some reason!!)
        camera_distance = (-v.get_draw_pos() - active_cam.get_pos()).mag()

        if camera_distance > 3000:
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()

        else:
            # actually render model now
            if draw_mode == 1 or draw_mode == 2:
                glPolygonMode(GL_FRONT, GL_FILL)
                glBegin(GL_POLYGON)
                for face in v.model.faces:
                    for i in range(3):
                        vertex_x = v.model.vertices[face[0][i]-1][0]
                        vertex_y = v.model.vertices[face[0][i]-1][1]
                        vertex_z = v.model.vertices[face[0][i]-1][2]
                        
                        glVertex3f(vertex_x, vertex_y, vertex_z)
                glEnd()
            if draw_mode == 0 or draw_mode == 2:
                glPolygonMode(GL_FRONT, GL_LINE)
                if draw_mode == 2:
                    # darken color a bit so that lines are actually visible
                    glColor(v.get_color()[0]/1.25, v.get_color()[1]/1.25, v.get_color()[2]/1.25)
                glBegin(GL_TRIANGLES)
                for face in v.model.faces:
                    for i in range(3):
                        vertex_x = v.model.vertices[face[0][i]-1][0]
                        vertex_y = v.model.vertices[face[0][i]-1][1]
                        vertex_z = v.model.vertices[face[0][i]-1][2]
                        
                        glVertex3f(vertex_x, vertex_y, vertex_z)
                glEnd()

        # now get out
        glPopMatrix()

def drawTrajectories(vessels, scene_lock):
    
    for v in vessels:
        if not v == scene_lock:
            # change color we render with
            glColor(v.get_color()[0], v.get_color()[1], v.get_color()[2])

            vertices = v.get_draw_traj_history()

            if len(vertices) > 3:
                glBegin(GL_LINE_STRIP)
                for i in range(1, len(vertices)):
                    # glVertex3f(vertices[i-1][0], vertices[i-1][1], vertices[i-1][2])
                    glVertex3f(vertices[i].x, vertices[i].y, vertices[i].z)
                glEnd()

def drawManeuvers(maneuvers, point_size, cam):

    for m in maneuvers:

        if m.type != "impulsive":

            if m.type == "const_accel":
                glColor(0.0, 1.0, 1.0)
            else: # const_thrust
                glColor(1.0, 1.0, 0.0)
                
            vertices = m.get_draw_vertices()

            if len(vertices) > 3:
                glBegin(GL_LINE_STRIP)
                for i in range(1, len(vertices)):
                    glVertex3f(vertices[i].x, vertices[i].y, vertices[i].z)
                glEnd()
                
        else:
            if m.get_draw_point():
                glColor(1.0, 0.0, 1.0)
                vertex = m.get_draw_point()
                cam_dist = (cam.get_pos() - vertex).mag()
                mnv_point_size = max(int(60000/cam_dist), 1)
                glPointSize(mnv_point_size)
                glBegin(GL_POINTS)
                glVertex3f(vertex.x, vertex.y, vertex.z)
                glEnd()
                glPointSize(point_size)

def drawProjections(projections):
    
    for p in projections:
        glColor(p.vessel.get_color()[0]/1.5, p.vessel.get_color()[1]/1.5, p.vessel.get_color()[2]/1.5)

        # draw dashed lines for trajectory

        vertices = p.get_draw_vertices()
            
        num_of_vertices = len(vertices)
        vertex_groups = []

        i = 0
        dash_skip_size = 20
        while i+dash_skip_size < len(vertices):
            vertex_groups.append([vertices[i] + p.get_body().get_pos() * visual_scaling_factor,
                                  vertices[i+dash_skip_size] + p.get_body().get_pos() * visual_scaling_factor])
            i += dash_skip_size

        for i in range(1, len(vertex_groups)-1, 2):
            glBegin(GL_LINES)
            glVertex3f(vertex_groups[i][0].x, vertex_groups[i][0].y, vertex_groups[i][0].z)
            glVertex3f(vertex_groups[i][1].x, vertex_groups[i][1].y, vertex_groups[i][1].z)
            glEnd()

        # draw lines to apoapsis and periapsis

        center = p.body.get_draw_pos()
        pe_adjusted = p.draw_pe + p.get_body().get_draw_pos()
        ap_adjusted = p.draw_ap + p.get_body().get_draw_pos()
        an_adjusted = p.draw_an + p.get_body().get_draw_pos()
        dn_adjusted = p.draw_dn + p.get_body().get_draw_pos()

        glBegin(GL_LINES)
        glVertex3f(center.x, center.y, center.z)
        glVertex3f(pe_adjusted.x, pe_adjusted.y, pe_adjusted.z)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(center.x, center.y, center.z)
        glVertex3f(ap_adjusted.x, ap_adjusted.y, ap_adjusted.z)
        glEnd()

        glColor(p.vessel.get_color()[0]/2, p.vessel.get_color()[1]/2, p.vessel.get_color()[2]/2)

        glBegin(GL_LINES)
        glVertex3f(center.x, center.y, center.z)
        glVertex3f(an_adjusted.x, an_adjusted.y, an_adjusted.z)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(center.x, center.y, center.z)
        glVertex3f(dn_adjusted.x, dn_adjusted.y, dn_adjusted.z)
        glEnd()

def drawSurfacePoints(surface_points, active_cam):

    for sp in surface_points:
        b = sp.get_body()

        camera_distance = (-b.get_draw_pos() - active_cam.get_pos()).mag()
        camera_physical_distance = camera_distance / visual_scaling_factor

        # only draw if the parent body does not appear too small on the screen

        if not math.degrees(math.atan(b.get_radius()*2/camera_physical_distance)) < 1.5:
            glColor(sp.get_color()[0], sp.get_color()[1], sp.get_color()[2])
            glPushMatrix()
            glTranslate(sp.get_draw_pos().x, sp.get_draw_pos().y, sp.get_draw_pos().z)
            glBegin(GL_POINTS)
            glVertex3f(0,0,0)
            glEnd()
            glPopMatrix()

def drawSurfaceCoverages(surface_coverages, active_cam):

    for sc in surface_coverages:
        if sc.b != None:
            camera_distance = (-sc.body.get_draw_pos() - active_cam.get_pos()).mag()
            camera_physical_distance = camera_distance / visual_scaling_factor

            # only draw if the body does not appear too small on the screen
            if math.degrees(math.atan(sc.body.get_radius()*2/camera_physical_distance)) < 1.5:
                return

            # calc. drawing centerpoint of circle
            center = sc.vessel.get_draw_pos() + sc.vessel.get_unit_vector_towards(sc.body) * sc.b * visual_scaling_factor

            if abs((sc.vessel.pos - sc.body.pos).normalized().dot(vec3(0, 1, 0))) < 1:
                plane_maker = vec3(0, 1, 0)
            else:
                plane_maker = vec3(1, 0, 0)

            axis = (sc.vessel.pos - sc.body.pos).normalized()
            h_vec0 = axis.cross(plane_maker)
            
            circle_poly = 256 # how many 'edges' a circle should have

            glColor(sc.vessel.get_color()[0], sc.vessel.get_color()[1], sc.vessel.get_color()[2])
            glPushMatrix()
            glBegin(GL_LINE_STRIP)
            for i in range(circle_poly + 1):
                theta = i / circle_poly * 2 * math.pi
                h_vec = h_vec0.rotate(axis, theta)
                point_pos = center + h_vec * sc.h * visual_scaling_factor
                glVertex3f(point_pos.x, point_pos.y, point_pos.z)

            glEnd()
            glPopMatrix()

def drawBarycenters(barycenters, active_cam):

    for bc in barycenters:

        cam_dist = (-bc.get_draw_pos() - active_cam.get_pos()).mag()
        crossline_length = cam_dist/6
        
        glColor(bc.get_color())
        glPushMatrix()
        glTranslate(bc.get_draw_pos().x, bc.get_draw_pos().y, bc.get_draw_pos().z)
        glBegin(GL_LINES)
        
        glVertex3f(-crossline_length/2, 0, 0)
        glVertex3f(crossline_length/2, 0, 0)

        glVertex3f(0, -crossline_length/2, 0)
        glVertex3f(0, crossline_length/2, 0)

        glVertex3f(0, 0, -crossline_length/2)
        glVertex3f(0, 0, crossline_length/2)

        glEnd()
        glPopMatrix()

def drawBarycenterLabels(bcs, cam, offset=0.05, far_clip=1e6):

    for bc in bcs:

        if world2cam(bc.get_pos().tolist(), cam):
            label_render_start = world2cam(bc.get_pos().tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(bc.get_name(), vector_scale(bc.get_color(), 2), label_render_start, cam, 0.1, far_clip)

def drawBodyLabels(bs, cam, offset=0.05, far_clip=1e6):

    for b in bs:

        if world2cam(b.get_pos().tolist(), cam):
            label_render_start = world2cam(b.get_pos().tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(b.get_name(), vector_scale(b.get_color(), 2), label_render_start, cam, 0.1, far_clip)

def drawSurfacePointLabels(sps, cam, offset=0.05, far_clip=1e6):

    for sp in sps:

        if world2cam(sp.get_pos(), cam):
            
            b = sp.get_body()

            camera_distance = (-b.get_draw_pos() - cam.get_pos()).mag()
            camera_physical_distance = camera_distance / visual_scaling_factor

            # only draw if the parent body does not appear too small on the screen

            if not math.degrees(math.atan(b.get_radius()*2/camera_physical_distance)) < 1.5:
                label_render_start = world2cam(sp.get_pos().tolist(), cam)
                label_render_start[0] += offset
                label_render_start[1] -= offset
                render_AN(sp.get_name(), vector_scale(sp.get_color(), 2), label_render_start, cam, 0.1, far_clip)

def drawVesselLabels(vs, cam, offset=0.05, far_clip=1e6):

    for v in vs:

        if world2cam(v.get_pos().tolist(), cam):
            label_render_start = world2cam(v.get_pos().tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(v.get_name(), vector_scale(v.get_color(), 2), label_render_start, cam, 0.1, far_clip)

def drawProjectionLabels(ps, cam, offset=0.05, size=0.05, far_clip=1e6):

    for p in ps:
        pe_adjusted = p.draw_pe + p.get_body().get_draw_pos()
        ap_adjusted = p.draw_ap + p.get_body().get_draw_pos()
        an_adjusted = p.draw_an + p.get_body().get_draw_pos()
        dn_adjusted = p.draw_dn + p.get_body().get_draw_pos()

        pe_adjusted = pe_adjusted / visual_scaling_factor
        ap_adjusted = ap_adjusted / visual_scaling_factor
        an_adjusted = an_adjusted / visual_scaling_factor
        dn_adjusted = dn_adjusted / visual_scaling_factor

        if world2cam(pe_adjusted, cam):
            label_render_start = world2cam(pe_adjusted.tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(("PERI " + str(p.get_periapsis_alt())), p.vessel.get_color(), label_render_start, cam, size, far_clip)

        if world2cam(ap_adjusted, cam):
            label_render_start = world2cam(ap_adjusted.tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(("APO " + str(p.get_apoapsis_alt())), p.vessel.get_color(), label_render_start, cam, size, far_clip)

        if world2cam(an_adjusted, cam):
            label_render_start = world2cam(an_adjusted.tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(("ASCN " + str(p.get_inclination())), p.vessel.get_color(), label_render_start, cam, size, far_clip)

        if world2cam(dn_adjusted, cam):
            label_render_start = world2cam(dn_adjusted.tolist(), cam)
            label_render_start[0] += offset
            label_render_start[1] -= offset
            render_AN(("DSCN " + str(p.get_inclination())), p.vessel.get_color(), label_render_start, cam, size, far_clip)

def drawStarfield(starfield, cam, far_clip):
    star_dist = far_clip * 0.5
    
    glPushMatrix()
    glColor(1, 1, 1)
    glTranslate(-cam.pos[0], -cam.pos[1], -cam.pos[2])
    glBegin(GL_POINTS)
    for s in starfield:
        glVertex3f(s[0] * star_dist, s[1] * star_dist, s[2] * star_dist)
        
    glEnd()
    glPopMatrix()

def drawRapidCompute(cam, size=0.2):
    render_AN("RAPID COMPUTE ACTIVE", (1,0,0), [-5, 0.5], cam, size)
    render_AN("PLEASE BE PATIENT", (1,0,0), [-3, -0.5], cam, size/1.5)

def drawScene(bodies, vessels, surface_points, barycenters, projections, maneuvers, surface_coverages, active_cam, show_trajectories=True, draw_mode=1,
              labels_visible=True, pmcs_visible=True, scene_lock=None, point_size=2, grid_active=False, polar_grid_active=False, scene_rot_target=None,
              starfield=[], far_clip=1e6):
    
    # sort the objects by their distance to the camera so we can draw the ones in the front last
    # and it won't look like a ridiculous mess on screen
    # (cam and object coord systems are opposite for some reason!!)
    bodies.sort(key=lambda x: (-x.get_draw_pos() - active_cam.get_pos()).mag(), reverse=True)
    vessels.sort(key=lambda x: (-x.get_draw_pos() - active_cam.get_pos()).mag(), reverse=True)
    surface_points.sort(key=lambda x: (-x.get_draw_pos() - active_cam.get_pos()).mag(), reverse=True)

    if starfield:
        drawStarfield(starfield, active_cam, far_clip)

    if draw_mode == 0:
        if grid_active:
            spacing = drawGridPlane(active_cam, bodies, vessels)

        if polar_grid_active:
            radial_spacing = drawPolarGridPlane(active_cam, bodies, vessels)

    # now we can draw, but make sure vessels behind the bodies are drawn in front too
    # for convenience
    drawBarycenters(barycenters, active_cam)
    drawBodies(bodies, active_cam, draw_mode, pmcs_visible)

    if draw_mode == 1 or draw_mode == 2:
        if grid_active:
            spacing = drawGridPlane(active_cam, bodies, vessels)

        if polar_grid_active:
            radial_spacing = drawPolarGridPlane(active_cam, bodies, vessels)
    
    drawSurfaceCoverages(surface_coverages, active_cam)
    drawSurfacePoints(surface_points, active_cam)
    drawVessels(vessels, active_cam, draw_mode)

    if labels_visible:
        glEnable(GL_LINE_SMOOTH)
        drawBarycenterLabels(barycenters, active_cam, 0.05, far_clip)
        drawBodyLabels(bodies, active_cam, 0.05, far_clip)
        drawSurfacePointLabels(surface_points, active_cam, 0.05, far_clip)
        drawVesselLabels(vessels, active_cam, 0.05, far_clip)
        glDisable(GL_LINE_SMOOTH)

    drawProjections(projections)
    if labels_visible:
        drawProjectionLabels(projections, active_cam, 0.05, 0.05, far_clip)
    # draw trajectory and predictions
    if show_trajectories:
        glEnable(GL_LINE_SMOOTH)
        drawTrajectories(vessels, scene_lock)
        drawManeuvers(maneuvers, point_size, active_cam)
        glDisable(GL_LINE_SMOOTH)

    if grid_active and spacing:
        spacing_exp = int(math.log(spacing, 10) + 0.5)
        render_AN("CARTEZIAN GRID 1e" + str(spacing_exp) + " M", (1, 0, 0), [-11.5, 5.5], active_cam, 0.1, far_clip)

    if polar_grid_active and radial_spacing:
        radial_spacing_exp = int(math.log(radial_spacing, 10) + 0.5)
        render_AN("RADIAL GRID 1e" + str(radial_spacing_exp) + " M", (1, 0, 0), [-11.5, 6.5], active_cam, 0.1, far_clip)

    if scene_rot_target:
        render_AN("ROTATING REFERENCE FRAME", (1, 0, 0), [-11.5, -5.5], active_cam, 0.1, far_clip)
