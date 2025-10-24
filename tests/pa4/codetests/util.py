def format_points(pts_set, cols):
    points = ""
    i = 0
    for pt in pts_set:
      points +=  "%-50s" % str(pt)
      if i % cols == 0:
        points += '\n'
      i += 1
    points += '\n'
    return points

def test_passed(expected, student_result):
    if len(expected) != len(student_result):
        return False
    found_all = []
    for e in expected:
        found_e = False
        for s in student_result:
            if abs(e - s) < 10E-2:
                found_e = True
        found_all.append(found_e)
    return not (False in found_all)