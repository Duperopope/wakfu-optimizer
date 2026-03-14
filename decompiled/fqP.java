/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  RU
 *  RW
 *  RX
 *  SA
 *  Sg
 *  Sj
 *  Sz
 *  aDU
 *  com.google.common.base.Function
 *  gq
 *  org.apache.log4j.Logger
 *  org.jetbrains.annotations.Nullable
 *  ym
 *  yq
 *  yr
 *  zh
 *  zk
 *  zm
 */
import com.google.common.base.Function;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import org.apache.log4j.Logger;
import org.jetbrains.annotations.Nullable;

public class fqP<S extends fqE>
extends Sg<S, ym>
implements gq<yq> {
    private static final Logger sVO = Logger.getLogger(fqP.class);
    private Function<zh, S> sVP;

    public fqP(Function<zh, S> function, short s, RW<S, ym> rW, RU<S> rU, boolean bl, boolean bl2, boolean bl3) {
        super(s, rW, rU, bl, bl2, bl3);
        this.sVP = function;
        this.a(Sj.bnT);
    }

    public fqP(short s, RW<S, ym> rW, RU<S> rU, boolean bl, boolean bl2, boolean bl3) {
        super(s, rW, rU, bl, bl2, bl3);
        this.a(Sj.bnT);
    }

    public boolean a(yq yq2) {
        if (this.bnI) {
            sVO.warn((Object)"Impossible d'ajouter l'information de quantit\u00e9 \u00e0 un RawSpellLevelInventory qui n'est pas pr\u00e9vu pour");
        }
        yq2.clear();
        Iterator iterator = this.iterator();
        while (iterator.hasNext()) {
            fqE fqE2 = (fqE)iterator.next();
            if (!fqE2.bfh()) continue;
            yr yr2 = new yr();
            if (!fqE2.d(yr2.alI)) {
                return false;
            }
            yq2.alH.add(yr2);
        }
        return true;
    }

    public zk gjd() {
        zm zm2 = zk.axT();
        Iterator iterator = this.iterator();
        while (iterator.hasNext()) {
            fqE fqE2 = (fqE)iterator.next();
            zm2.d(fqE2.giQ());
        }
        return zm2.axZ();
    }

    public boolean b(yq yq2) {
        this.beQ();
        if (this.bnI) {
            sVO.warn((Object)"Impossible d'ajouter les quantit\u00e9s depuis un RawStackInventory qui ne connait pas cette information");
        }
        boolean bl = true;
        fqE fqE2 = null;
        if (this.bnG == null) {
            return false;
        }
        for (yr yr2 : yq2.alH) {
            try {
                fqE2 = (fqE)this.bnG.x((Object)yr2.alI);
                if (fqE2 != null) {
                    if (this.b(fqE2)) continue;
                    bl = false;
                    sVO.error((Object)("Unable to add spell " + fqE2.avr() + "to spell inventory"));
                    fqE2.aZp();
                    continue;
                }
                bl = false;
            }
            catch (SA sA) {
                sVO.error((Object)aDU.a((Throwable)sA));
                bl = false;
                fqE2.aZp();
            }
            catch (Sz sz) {
                sVO.error((Object)aDU.a((Throwable)sz));
                bl = false;
                fqE2.aZp();
            }
        }
        return bl;
    }

    public boolean g(zk zk2) {
        this.beQ();
        boolean bl = true;
        List list = zk2.axP();
        for (zh zh2 : list) {
            fqE fqE2 = (fqE)this.sVP.apply((Object)zh2);
            if (fqE2 == null) continue;
            try {
                if (this.b(fqE2)) continue;
                bl = false;
                sVO.error((Object)("Unable to add spell " + zh2.axA() + "to spell inventory"));
                fqE2.aZp();
            }
            catch (SA | Sz throwable) {
                sVO.error((Object)("Failed to add " + String.valueOf(fqE2.sUL) + " to inventory"), throwable);
                bl = false;
                fqE2.aZp();
            }
        }
        return bl;
    }

    public HashMap<Long, S> gje() {
        return this.bnF;
    }

    public int pa(int n) {
        return 0;
    }

    public int a(int n, int n2, boolean bl) {
        return 0;
    }

    @Nullable
    public S gjf() {
        Iterator iterator = this.bnF.values().iterator();
        if (iterator.hasNext()) {
            fqE fqE2 = (fqE)iterator.next();
            return (S)fqE2;
        }
        return null;
    }

    public ArrayList<S> b(RX rX) {
        return super.b(rX);
    }
}
